"""
ToolRegistry — the single place every available tool is registered.

Agents query this registry by tool name. The adaptation pipeline remains
tool-agnostic: it reads a ToolDefinition and works with its contracts.

Weather is NOT registered here yet — that happens in Step 3, where we
wrap the existing weather implementation behind this registry without
changing its behavior.
"""

from typing import Dict, List
from .base import ToolDefinition


class ToolRegistry:
    """In-memory registry of every tool the agent can adapt to."""

    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' is already registered.")
        self._tools[tool.name] = tool

    def get(self, name: str) -> ToolDefinition:
        if name not in self._tools:
            raise KeyError(
                f"Unknown tool '{name}'. "
                f"Registered: {list(self._tools.keys())}"
            )
        return self._tools[name]

    def has(self, name: str) -> bool:
        return name in self._tools

    def all_names(self) -> List[str]:
        return list(self._tools.keys())

    def all_tools(self) -> List[ToolDefinition]:
        return list(self._tools.values())

    def to_list(self) -> List[Dict]:
        return [t.to_dict() for t in self._tools.values()]


# Single global instance. Tools register themselves against this.
tool_registry = ToolRegistry()
