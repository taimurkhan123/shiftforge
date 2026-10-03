from pydantic import BaseModel, Field
from typing import Any, Dict, Optional


class ToolContract(BaseModel):
    """Describes the shape of an external tool/API the agent depends on."""
    version: str
    endpoint: str
    method: str = "GET"
    temperature_field: str
    condition_field: str

    def matches(self, other: "ToolContract") -> bool:
        return (
            self.endpoint == other.endpoint
            and self.temperature_field == other.temperature_field
            and self.condition_field == other.condition_field
        )


class ToolResponse(BaseModel):
    """Normalized response shape the agent expects."""
    temperature: float
    condition: str
    raw: Dict[str, Any] = Field(default_factory=dict)


class ContractMismatch(Exception):
    """Raised when a tool response does not match the expected contract."""
    def __init__(self, reason: str, payload: Optional[Dict[str, Any]] = None):
        super().__init__(reason)
        self.reason = reason
        self.payload = payload or {}