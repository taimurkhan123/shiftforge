"""
Generic strategy model — supports any tool, not just weather.
"""

from typing import Dict, Any
from pydantic import BaseModel, Field


class GenericStrategySpec(BaseModel):
    """A strategy for any tool. Fields are dynamic field-name mappings."""
    version: str
    endpoint: str
    method: str = "GET"
    fields: Dict[str, str] = Field(default_factory=dict)
    reasoning: str = ""
