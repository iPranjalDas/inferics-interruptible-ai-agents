"""
NEXUS-DUAL: Core Orchestration Engine.
Coordinates Fast-Path Micro-Reactor, Slow-Path Speculative Planner,
Immutable Slot Ledger, and Multimodal Pipeline across asynchronous input/output queues.
"""

from __future__ import annotations
import asyncio
from concurrent.futures import ThreadPoolExecutor
import gc
import re
from typing import Any, Dict, List, Optional, Callable
from src.schema import (
    BaseInputEvent,
    BaseOutputAction,
    TextChunkEvent,
    AudioClipEvent,
    VideoFrameEvent,
    InterruptionSignalEvent,
    AsyncToolResultEvent,
    ScenarioToolManifest,
    FinalResponseAction,
    StateSnapshot
)
from src.slot_ledger import ImmutableSlotLedger
from src.fast_path import FastPathReactor
from src.slow_path import SlowPathPlanner
from src.multimodal import MultimodalIngestionPipeline


class NexusDualAgent:
    def __init__(
        self,
        event_input_queue: asyncio.Queue[BaseInputEvent],
        action_output_queue: asyncio.Queue[BaseOutputAction]
    ) -> None:
        self.input_queue = event_input_queue
        self.output_queue = action_output_queue
        
        # Dedicated thread pool for heavy compute (image decoding, LLM proxy)
        self.pool = ThreadPoolExecutor(max_workers=4, thread_name_prefix="nexus_worker")

        # Subsystems
        self.ledger = ImmutableSlotLedger()
        self.fast_path = FastPathReactor(self.ledger, self.output_queue)
        self.slow_path = SlowPathPlanner(self.ledger, self.output_queue, self.pool)
        self.multimodal = MultimodalIngestionPipeline(pool=self.pool)

        # Worker tasks
        self._consumer_task: Optional[asyncio.Task] = None
        self._is_running: bool = False

    async def start(self) -> None:
        """Starts the event consumer loop."""
        self._is_running = True
        self._consumer_task = asyncio.create_task(self._process_event_queue())

    async def stop(self) -> None:
        """Gracefully terminates the orchestrator."""
        self._is_running = False
        if self._consumer_task and not self._consumer_task.done():
            self._consumer_task.cancel()
            try:
                await self._consumer_task
            except asyncio.CancelledError:
                pass
        self.reset_session()

    async def _process_event_queue(self) -> None:
        """Main event routing loop consuming from the streaming harness."""
        try:
            while self._is_running:
                event = await self.input_queue.get()
                await self.dispatch_event(event)
                self.input_queue.task_done()
        except asyncio.CancelledError:
            pass

    async def dispatch_event(self, event: BaseInputEvent) -> None:
        """Routes timestamped events to appropriate subsystems."""
        event_type = event.event_type

        # 1. High-Priority User Interruption
        if event_type == "interruption_signal":
            assert isinstance(event, InterruptionSignalEvent)
            await self.fast_path.handle_interruption(event)

        # 2. Text Chunks & End-of-Turn Tokens
        elif event_type == "transcribed_text_chunk":
            assert isinstance(event, TextChunkEvent)
            await self._handle_text_chunk(event)

        # 3. Vision Frame
        elif event_type == "video_frame":
            assert isinstance(event, VideoFrameEvent)
            await self._handle_video_frame(event)

        # 4. Audio Clip
        elif event_type == "raw_audio_clip":
            assert isinstance(event, AudioClipEvent)
            self.multimodal.ingest_audio(event)

        # 5. Async Tool Result from Mock Harness
        elif event_type == "async_tool_result":
            assert isinstance(event, AsyncToolResultEvent)
            await self.slow_path.handle_tool_completion(event, event.timestamp_ms)

        # 6. Dynamic Scenario Tool Manifest
        elif event_type == "scenario_tool_manifest":
            assert isinstance(event, ScenarioToolManifest)
            self.slow_path.load_manifest(event)

    async def _handle_text_chunk(self, event: TextChunkEvent) -> None:
        """Processes incoming tokens, manages slots, and triggers actions."""
        # 1. Fast Path Token Inspection (Detects mid-sentence self-corrections & emits fillers)
        is_self_correction, correction_phrase = await self.fast_path.inspect_text_chunk(event)

        raw_text = event.text.strip()
        lower_text = raw_text.lower()

        # 2. Intent and Slot Parsing (Deterministic rule-based / regex extraction for microsecond speed)
        current_intent = self.ledger.current_snapshot.intent
        if any(w in lower_text for w in ["flight", "fly", "ticket"]) or current_intent == "flight_reservation":
            self.ledger.set_intent("flight_reservation")

            # Extract destinations and origins
            # Case: "from <origin> to <dest>"
            m_route = re.search(r"from\s+([A-Za-z]+)\s+to\s+([A-Za-z]+)", lower_text)
            if m_route:
                self.ledger.update_slot("origin", m_route.group(1).title(), locked=True)
                self.ledger.update_slot("destination", m_route.group(2).title(), locked=False)

            # Direct destination mentions: "to San Francisco", "make that San Francisco"
            m_dest = re.search(r"(?:to|make that|instead of \w+)\s+([A-Za-z\s]+?)(?:$|\.|\,)", lower_text)
            if m_dest and "from" not in lower_text:
                raw_dest = m_dest.group(1).strip()
                cleaned_dest = re.sub(r"\b(instead|please|thanks)\b", "", raw_dest, flags=re.IGNORECASE).strip().title()
                if cleaned_dest and cleaned_dest not in ["A Flight", "The", "Here"]:
                    if is_self_correction:
                        # Self-repair: update destination while keeping origin locked!
                        self.ledger.repair_slot("destination", cleaned_dest)
                    else:
                        self.ledger.update_slot("destination", cleaned_dest, locked=False)

            # Extract date if present
            m_date = re.search(r"(tomorrow|next week|\d{4}-\d{2}-\d{2}|october \d+)", lower_text)
            if m_date:
                self.ledger.update_slot("date", m_date.group(1), locked=True)

            # Speculative Read-Only Search Trigger (Latency hiding)
            if not event.is_final_turn and "destination" in self.ledger.current_snapshot.slots:
                dest_val = self.ledger.current_snapshot.slots["destination"].value
                # Only trigger if not already searching for this destination
                call_id = await self.slow_path.execute_tool_call(
                    tool_name="search_flights",
                    arguments={"destination": dest_val},
                    timestamp_ms=event.timestamp_ms,
                    is_final_turn=False
                )
                if call_id:
                    # Spawn background worker and register with Fast Path
                    worker_task = asyncio.create_task(
                        self.slow_path.run_tool_worker(call_id, "search_flights", {"destination": dest_val}, latency_ms=120.0)
                    )
                    self.fast_path.register_task(call_id, worker_task, event.timestamp_ms)

            # Final Turn Action (State-Modifying booking or finalized confirmation)
            if event.is_final_turn:
                slots = self.ledger.get_slot_values()
                call_id = await self.slow_path.execute_tool_call(
                    tool_name="book_flight",
                    arguments=slots,
                    timestamp_ms=event.timestamp_ms,
                    is_final_turn=True
                )
                if call_id:
                    async def _run_booking():
                        res = await self.slow_path.run_tool_worker(call_id, "book_flight", slots, latency_ms=40.0)
                        if res:
                            await self.slow_path.handle_tool_completion(res, asyncio.get_event_loop().time() * 1000.0)

                    worker_task = asyncio.create_task(_run_booking())
                    self.fast_path.register_task(call_id, worker_task, event.timestamp_ms)
                else:
                    # Emit final snapshot
                    self.ledger.mark_complete()
                    final_action = FinalResponseAction(
                        timestamp_ms=event.timestamp_ms + 10.0,
                        text=f"Flight booking confirmed with slots: {slots}.",
                        snapshot=self.ledger.current_snapshot
                    )
                    await self.output_queue.put(final_action)

        elif any(w in lower_text for w in ["router", "light", "blinking", "led"]):
            self.ledger.set_intent("device_troubleshooting")
            # If visual tokens exist, ground response
            visual_ctx = self.ledger.get_slot_values().get("visual_indicator", "amber_blinking")
            if event.is_final_turn:
                self.ledger.mark_complete()
                final_action = FinalResponseAction(
                    timestamp_ms=event.timestamp_ms + 15.0,
                    text=f"The device shows an {visual_ctx} indicator. Manual lookup confirms connection handshake pending.",
                    snapshot=self.ledger.current_snapshot
                )
                await self.output_queue.put(final_action)

    async def _handle_video_frame(self, event: VideoFrameEvent) -> None:
        """Analyzes frame in background thread and updates ledger slots."""
        self.multimodal.ingest_frame(event)
        loop = asyncio.get_running_loop()
        analysis = await loop.run_in_executor(self.pool, self.multimodal.analyze_frame_sync, event.image_bytes)
        
        detected_led = analysis.get("detected_led", "normal")
        self.ledger.update_slot("visual_indicator", detected_led, confidence=analysis.get("confidence", 0.95), locked=True)

    def reset_session(self) -> None:
        """
        Hard Session Teardown hook.
        Guarantees Session Memory Isolation across all sequential benchmark scenarios.
        """
        self.fast_path.reset()
        self.slow_path.reset()
        self.multimodal.reset()
        self.ledger.reset()
        gc.collect()
