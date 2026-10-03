"""
Generic executor — runs a strategy against any registered tool.

Reads a ToolScenario.contract (generic dict of *_field keys), validates
the strategy against it, and calls the scenario's simulator.

No hardcoded weather logic. Works for any registered tool.
"""

from typing import Dict, Any, Optional
from app.tools.registry import tool_registry


class GenericStrategyError(Exception):
    """Raised when a strategy cannot execute against the current tool scenario."""
    def __init__(self, message: str, payload: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.payload = payload or {}


def _extract_field_keys(contract: Dict[str, Any]) -> Dict[str, str]:
    """Return {'temperature_field': 'temperature', ...} from a contract."""
    return {k: v for k, v in contract.items() if k.endswith("_field")}


def execute_generic_strategy(tool_name: str, strategy_endpoint: str, strategy_fields: Dict[str, str]) -> Dict[str, Any]:
    """
    Execute a strategy against the current active scenario of a tool.

    strategy_fields: mapping of contract field key -> field name (e.g. {"temperature_field": "temperature"}).
    Raises GenericStrategyError on mismatch.
    """
    if not tool_registry.has(tool_name):
        raise GenericStrategyError(f"Unknown tool: {tool_name}")

    tool = tool_registry.get(tool_name)
    scenario = tool.active_scenario
    contract = scenario.contract
    expected_endpoint = contract.get("endpoint")

    if strategy_endpoint != expected_endpoint:
        raise GenericStrategyError(
            f"Endpoint mismatch: strategy='{strategy_endpoint}' vs tool='{expected_endpoint}'",
            payload={"expected": expected_endpoint, "actual": strategy_endpoint},
        )

    expected_fields = _extract_field_keys(contract)
    for key, expected_value in expected_fields.items():
        actual_value = strategy_fields.get(key)
        if actual_value != expected_value:
            raise GenericStrategyError(
                f"Field mismatch on '{key}': strategy='{actual_value}' vs tool='{expected_value}'",
                payload={"field": key, "expected": expected_value, "actual": actual_value},
            )

    try:
        raw = scenario.simulate()
    except Exception as e:
        raise GenericStrategyError(f"Simulator failed: {e}", payload={"raw": None})

    return {"tool": tool_name, "version": tool.active_version, "raw": raw}
