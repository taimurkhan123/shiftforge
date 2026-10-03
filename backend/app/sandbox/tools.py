"""
Controlled tool registry.

The agent can ONLY call tools listed here, by name.
No eval, no exec, no dynamic imports.

Each tool receives the environment contract version it must serve,
and returns a raw payload shaped for that version.
"""

from typing import Any, Dict, Callable
from app.models.contract import ContractMismatch


# Simulated "backend" data — the actual weather truth
_TRUTH = {"temperature_c": 28, "condition": "Sunny"}


def _serve_v1() -> Dict[str, Any]:
    """Original /api/weather response shape."""
    return {
        "temperature": _TRUTH["temperature_c"],
        "condition": _TRUTH["condition"],
    }


def _serve_v2() -> Dict[str, Any]:
    """New /api/forecast response shape."""
    return {
        "temp_c": _TRUTH["temperature_c"],
        "weather": _TRUTH["condition"],
    }


TOOL_REGISTRY: Dict[str, Callable[[], Dict[str, Any]]] = {
    "fetch_weather_v1": _serve_v1,
    "fetch_weather_v2": _serve_v2,
}


def call_tool(tool_name: str) -> Dict[str, Any]:
    """
    Invoke a registered tool by name.
    Raises ContractMismatch if the tool is not registered (safety).
    """
    fn = TOOL_REGISTRY.get(tool_name)
    if fn is None:
        raise ContractMismatch(
            reason=f"Tool '{tool_name}' is not registered. Refusing to execute.",
            payload={"available": list(TOOL_REGISTRY.keys())},
        )
    return fn()