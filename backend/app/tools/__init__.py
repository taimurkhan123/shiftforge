"""
ShiftForge Tool Registry.

Safe, multi-tool abstraction layer. Weather is wrapped here as the first
registered tool. New tools (GitHub, Database, Custom) plug in without
changing the existing adaptation pipeline.
"""

from .base import ToolDefinition, ToolScenario
from .registry import ToolRegistry, tool_registry

__all__ = [
    "ToolDefinition",
    "ToolScenario",
    "ToolRegistry",
    "tool_registry",
]
