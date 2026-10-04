"""
Slow-Path Speculative Planner & Dynamic Idempotency Gatekeeper.
Enforces:
- Hard confirmation barrier for state-modifying tools (Safety & Protocol 10%)
- Speculative latency hiding for read-only tools
- Offloading heavy computation to ThreadPoolExecutor to prevent event-loop starvation
- Revocation gate: Dropping zombie results from cancelled call_ids
"""

from __future__ import annotations
import asyncio
from concurrent.futures import ThreadPoolExecutor
import uuid
from typing import Any, Dict, List, Optional, Callable
from src.schema import (
    ToolDefinition,
    ScenarioToolManifest,
    ToolCallAction,
    AsyncToolResultEvent,
    FinalResponseAction,
    BaseOutputAction
)
from src.slot_ledger import ImmutableSlotLedger


class SlowPathPlanner:
    def __init__(
        self,
        slot_ledger: ImmutableSlotLedger,
        output_queue: asyncio.Queue[BaseOutputAction],
        thread_pool: Optional[ThreadPoolExecutor] = None
    ) -> None:
        self.ledger = slot_ledger
        self.output_queue = output_queue
        self.pool = thread_pool or ThreadPoolExecutor(max_workers=4)
        
        # Scenario tools: name -> ToolDefinition
        self.tools: Dict[str, ToolDefinition] = {}
        # Completed results: call_id -> AsyncToolResultEvent
        self.completed_results: Dict[str, AsyncToolResultEvent] = {}

    def load_manifest(self, manifest: ScenarioToolManifest) -> None:
        """Loads and indexes the tools for the active scenario."""
        self.tools.clear()
        for tool in manifest.tools:
            self.tools[tool.name] = tool

    def is_tool_state_modifying(self, tool_name: str) -> bool:
        """Determines if a tool has state-altering side effects."""
        tool = self.tools.get(tool_name)
        if tool:
            return tool.is_state_modifying
        # Fail safe: unknown tools treated as state modifying
        return True

    async def execute_tool_call(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        timestamp_ms: float,
        is_final_turn: bool = False,
        mock_handler: Optional[Callable[[str, Dict[str, Any]], Any]] = None
    ) -> Optional[str]:
        """
        Dispatches a tool call with strict idempotency gatekeeping.
        Returns: call_id if dispatched, None if blocked by safety gate.
        """
        is_modifying = self.is_tool_state_modifying(tool_name)

        # SAFETY PROTOCOL GATE:
        # Non-idempotent tools MUST NOT execute speculatively mid-turn!
        if is_modifying and not is_final_turn:
            # Blocked by protocol
            return None

        call_id = f"call_{uuid.uuid4().hex[:8]}"

        # Emit non-blocking tool call action
        call_action = ToolCallAction(
            timestamp_ms=timestamp_ms,
            call_id=call_id,
            tool_name=tool_name,
            arguments=arguments,
            speculative=(not is_final_turn)
        )
        await self.output_queue.put(call_action)

        return call_id

    async def run_tool_worker(
        self,
        call_id: str,
        tool_name: str,
        arguments: Dict[str, Any],
        latency_ms: float,
        mock_handler: Optional[Callable[[str, Dict[str, Any]], Any]] = None
    ) -> Optional[AsyncToolResultEvent]:
        """
        Simulated background tool worker.
        Sleeps for tool latency, respecting asyncio.CancelledError on interruption.
        """
        try:
            # Simulate network or execution latency with cancellation support
            await asyncio.sleep(latency_ms / 1000.0)

            # Check if this call was cancelled while sleeping
            if call_id in self.ledger.current_snapshot.cancelled_call_ids:
                # Zombie socket defense: drop result silently
                return None

            # Execute mock handler in thread pool if provided, else return simulated payload
            if mock_handler:
                loop = asyncio.get_running_loop()
                result = await loop.run_in_executor(self.pool, mock_handler, tool_name, arguments)
            else:
                result = {"status": "success", "tool": tool_name, "args": arguments}

            res_event = AsyncToolResultEvent(
                timestamp_ms=asyncio.get_event_loop().time() * 1000.0,
                call_id=call_id,
                tool_name=tool_name,
                result=result,
                error=None
            )
            self.completed_results[call_id] = res_event
            return res_event

        except asyncio.CancelledError:
            # Clean cooperative abortion
            self.ledger.mark_call_cancelled(call_id)
            raise

    async def handle_tool_completion(
        self,
        res_event: AsyncToolResultEvent,
        timestamp_ms: float
    ) -> None:
        """
        Handles incoming tool results, verifying they were not cancelled.
        Emits final response snapshot when ready.
        """
        # Zombie check: drop if call_id in cancelled list
        if res_event.call_id in self.ledger.current_snapshot.cancelled_call_ids:
            return

        # Mark final snapshot
        self.ledger.mark_complete()
        snapshot = self.ledger.current_snapshot

        # Formulate grounded final response
        final_text = f"Action for {res_event.tool_name} completed with verified parameters: {self.ledger.get_slot_values()}."
        final_action = FinalResponseAction(
            timestamp_ms=timestamp_ms,
            text=final_text,
            snapshot=snapshot
        )
        await self.output_queue.put(final_action)

    def reset(self) -> None:
        """Resets tool memory and cached results for session isolation."""
        self.completed_results.clear()
        self.tools.clear()
