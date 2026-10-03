from enum import Enum
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class RunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    CHANGE_DETECTED = "change_detected"
    DIAGNOSING = "diagnosing"
    STRATEGIZING = "strategizing"
    SANDBOXING = "sandboxing"
    VALIDATING = "validating"
    RECOVERING = "recovering"
    SUCCESS = "success"
    FAILED = "failed"


class RunStep(BaseModel):
    """A single step in the adaptation timeline."""
    stage: str
    status: str  # running | success | warning | failed
    message: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    duration_ms: Optional[int] = None
    data: Dict[str, Any] = Field(default_factory=dict)


class RunState(BaseModel):
    """Full state of a single agent run."""
    run_id: str
    task: str
    status: RunStatus = RunStatus.PENDING
    environment_version: str = "v1"
    initial_strategy_version: str = "weather_v1"
    final_strategy_version: Optional[str] = None
    steps: List[RunStep] = Field(default_factory=list)
    result: Optional[Dict[str, Any]] = None
    failure_reason: Optional[str] = None
    total_adaptation_ms: Optional[int] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
