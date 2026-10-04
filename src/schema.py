"""
Data contracts and event schemas for the Samsung Theme 05 benchmark.
Adheres strictly to the Virtual Clock Streaming Interface Contract.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field


# ============================================================================
# TOOL MANIFEST SCHEMAS
# ============================================================================

class ToolParameter(BaseModel):
    name: str
    type: str
    description: str
    required: bool = True


class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    is_state_modifying: bool = False  # Critical gate: never run speculatively if True
    simulated_latency_ms: float = 100.0


class ScenarioToolManifest(BaseModel):
    scenario_id: str
    tools: List[ToolDefinition] = Field(default_factory=list)


# ============================================================================
# INPUT STREAMING EVENT CONTRACTS
# ============================================================================

class BaseInputEvent(BaseModel):
    timestamp_ms: float
    event_type: str


class TextChunkEvent(BaseInputEvent):
    event_type: Literal["transcribed_text_chunk"] = "transcribed_text_chunk"
    text: str
    is_final_turn: bool = False
    confidence: float = 1.0


class AudioClipEvent(BaseInputEvent):
    event_type: Literal["raw_audio_clip"] = "raw_audio_clip"
    audio_bytes: Optional[bytes] = None
    duration_ms: float = 0.0
    format: str = "wav"


class VideoFrameEvent(BaseInputEvent):
    event_type: Literal["video_frame"] = "video_frame"
    frame_id: str
    image_bytes: Optional[bytes] = None
    width: int = 1920
    height: int = 1080


class InterruptionSignalEvent(BaseInputEvent):
    event_type: Literal["interruption_signal"] = "interruption_signal"
    reason: str = "user_speech_detected"
    detected_energy: float = 0.85


class AsyncToolResultEvent(BaseInputEvent):
    event_type: Literal["async_tool_result"] = "async_tool_result"
    call_id: str
    tool_name: str
    result: Any = None
    error: Optional[str] = None


# ============================================================================
# OUTPUT ACTION CONTRACTS (BENCHMARK SCORING TARGETS)
# ============================================================================

class BaseOutputAction(BaseModel):
    timestamp_ms: float
    action_type: str


class SpokenFillerAction(BaseOutputAction):
    """Emitted by Fast Path to collapse Time To First Spoken Action (Latency 15%)."""
    action_type: Literal["spoken_filler"] = "spoken_filler"
    text: str
    context_intent: str = "general_acknowledgement"


class ToolCallAction(BaseOutputAction):
    """Dispatched non-blocking tool execution with explicit call_id."""
    action_type: Literal["non_blocking_tool_call"] = "non_blocking_tool_call"
    call_id: str
    tool_name: str
    arguments: Dict[str, Any]
    speculative: bool = False


class CancellationAction(BaseOutputAction):
    """Sub-15ms cancellation emitted immediately upon interruption (Interruption Recovery 35%)."""
    action_type: Literal["cancellation"] = "cancellation"
    call_id: str
    reason: str = "user_interruption"
    elapsed_before_cancel_ms: float = 0.0


class ClarificationAction(BaseOutputAction):
    """Emitted when multimodal inputs or user commands are ambiguous."""
    action_type: Literal["clarification_request"] = "clarification_request"
    question: str
    missing_slots: List[str] = Field(default_factory=list)


class SlotValue(BaseModel):
    value: Any
    confidence: float = 1.0
    locked: bool = False  # If true, preserved across self-repairs unless explicitly invalidated
    version_set: int = 1


class StateSnapshot(BaseModel):
    version: int
    intent: Optional[str] = None
    slots: Dict[str, SlotValue] = Field(default_factory=dict)
    is_complete: bool = False
    active_call_ids: List[str] = Field(default_factory=list)
    cancelled_call_ids: List[str] = Field(default_factory=list)


class FinalResponseAction(BaseOutputAction):
    """Final grounded assistant response emitted with full verified state snapshot."""
    action_type: Literal["final_response_snapshot"] = "final_response_snapshot"
    text: str
    snapshot: StateSnapshot
