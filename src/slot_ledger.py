"""
Immutable Slot Ledger with Atomic Rollbacks & Self-Repair.
Maintains session state as a versioned DAG to eliminate stale hallucinations
and enable instant slot repair upon conversational interruptions.
"""

from __future__ import annotations
import copy
from typing import Any, Dict, List, Optional
from src.schema import StateSnapshot, SlotValue


class ImmutableSlotLedger:
    def __init__(self) -> None:
        self._history: List[StateSnapshot] = []
        self._current_version: int = 1
        
        # Initial empty snapshot
        initial_snapshot = StateSnapshot(
            version=1,
            intent=None,
            slots={},
            is_complete=False,
            active_call_ids=[],
            cancelled_call_ids=[]
        )
        self._history.append(initial_snapshot)

    @property
    def current_version(self) -> int:
        return self._current_version

    @property
    def current_snapshot(self) -> StateSnapshot:
        return self._history[-1]

    def set_intent(self, intent: str) -> StateSnapshot:
        """Sets or updates the primary conversational intent in a new snapshot version."""
        prev = self.current_snapshot
        if prev.intent == intent:
            return prev

        self._current_version += 1
        new_slots = copy.deepcopy(prev.slots)
        new_snapshot = StateSnapshot(
            version=self._current_version,
            intent=intent,
            slots=new_slots,
            is_complete=prev.is_complete,
            active_call_ids=list(prev.active_call_ids),
            cancelled_call_ids=list(prev.cancelled_call_ids)
        )
        self._history.append(new_snapshot)
        return new_snapshot

    def update_slot(
        self,
        key: str,
        value: Any,
        confidence: float = 1.0,
        locked: bool = False
    ) -> StateSnapshot:
        """Stages or updates a single slot value, creating a new ledger version."""
        prev = self.current_snapshot
        self._current_version += 1

        new_slots = copy.deepcopy(prev.slots)
        new_slots[key] = SlotValue(
            value=value,
            confidence=confidence,
            locked=locked,
            version_set=self._current_version
        )

        new_snapshot = StateSnapshot(
            version=self._current_version,
            intent=prev.intent,
            slots=new_slots,
            is_complete=False,
            active_call_ids=list(prev.active_call_ids),
            cancelled_call_ids=list(prev.cancelled_call_ids)
        )
        self._history.append(new_snapshot)
        return new_snapshot

    def repair_slot(
        self,
        key: str,
        new_value: Any,
        confidence: float = 1.0
    ) -> StateSnapshot:
        """
        Self-Repair Dynamics:
        Repairs a single invalidated slot while keeping all other locked/verified slots intact.
        Example: 'Book to Seattle... wait make that San Francisco' -> origin & date preserved.
        """
        prev = self.current_snapshot
        self._current_version += 1

        new_slots = copy.deepcopy(prev.slots)
        new_slots[key] = SlotValue(
            value=new_value,
            confidence=confidence,
            locked=True,
            version_set=self._current_version
        )

        new_snapshot = StateSnapshot(
            version=self._current_version,
            intent=prev.intent,
            slots=new_slots,
            is_complete=False,
            active_call_ids=list(prev.active_call_ids),
            cancelled_call_ids=list(prev.cancelled_call_ids)
        )
        self._history.append(new_snapshot)
        return new_snapshot

    def rollback_to_version(self, target_version: int) -> StateSnapshot:
        """
        Rolls back the ledger state to an earlier snapshot before the interrupted change.
        Returns the restored snapshot.
        """
        for snap in reversed(self._history):
            if snap.version <= target_version:
                self._current_version += 1
                restored = StateSnapshot(
                    version=self._current_version,
                    intent=snap.intent,
                    slots=copy.deepcopy(snap.slots),
                    is_complete=False,
                    active_call_ids=list(snap.active_call_ids),
                    cancelled_call_ids=list(self.current_snapshot.cancelled_call_ids)
                )
                self._history.append(restored)
                return restored
        
        # Fallback to base version if not found
        return self.current_snapshot

    def record_active_call(self, call_id: str) -> None:
        """Tracks an active in-flight tool call ID."""
        snap = self.current_snapshot
        if call_id not in snap.active_call_ids:
            snap.active_call_ids.append(call_id)

    def mark_call_cancelled(self, call_id: str) -> None:
        """Marks a call as cancelled and removes it from active list."""
        snap = self.current_snapshot
        if call_id in snap.active_call_ids:
            snap.active_call_ids.remove(call_id)
        if call_id not in snap.cancelled_call_ids:
            snap.cancelled_call_ids.append(call_id)

    def mark_complete(self) -> StateSnapshot:
        """Locks the final snapshot upon valid task completion."""
        prev = self.current_snapshot
        self._current_version += 1
        new_snapshot = StateSnapshot(
            version=self._current_version,
            intent=prev.intent,
            slots=copy.deepcopy(prev.slots),
            is_complete=True,
            active_call_ids=[],
            cancelled_call_ids=list(prev.cancelled_call_ids)
        )
        self._history.append(new_snapshot)
        return new_snapshot

    def get_slot_values(self) -> Dict[str, Any]:
        """Convenience method returning raw dict of slot values."""
        return {k: v.value for k, v in self.current_snapshot.slots.items()}

    def reset(self) -> None:
        """Full session cleanup to satisfy strict Session Memory Isolation."""
        self._history.clear()
        self._current_version = 1
        initial_snapshot = StateSnapshot(
            version=1,
            intent=None,
            slots={},
            is_complete=False,
            active_call_ids=[],
            cancelled_call_ids=[]
        )
        self._history.append(initial_snapshot)
