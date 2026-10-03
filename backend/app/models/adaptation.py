from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class MonitorResult(BaseModel):
    """Output from Monitor Agent."""
    status: str  # "ok" | "change_detected"
    severity: str = "low"  # low | medium | high
    reason: str = ""


class DiagnosisResult(BaseModel):
    """Output from Diagnosis Agent."""
    removed_fields: List[str] = Field(default_factory=list)
    added_fields: List[str] = Field(default_factory=list)
    endpoint_changed_from: Optional[str] = None
    endpoint_changed_to: Optional[str] = None
    summary: str = ""


class StrategySpec(BaseModel):
    """A structured strategy the agent can execute. LLM produces this."""
    version: str
    endpoint: str
    method: str = "GET"
    temperature_field: str
    condition_field: str
    reasoning: str = ""


class SandboxResult(BaseModel):
    """Output from Sandbox Agent."""
    executed: bool
    passed: bool
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ValidationResult(BaseModel):
    """Output from Validation Agent."""
    validated: bool
    confidence: float = 0.0
    reason: str = ""