"""
Generic sandbox — tests a strategy against any tool's active scenario.

Uses the same ToolScenario.contract validation as the generic executor,
but runs safely in isolation and returns a structured pass/fail result.

No hardcoded weather logic.
"""

from typing import Dict, Any, Optional
from app.models.adaptation import SandboxResult
from app.tools.registry import tool_registry


def _extract_field_keys(contract: Dict[str, Any]) -> Dict[str, str]:
    return {k: v for k, v in contract.items() if k.endswith("_field")}


def run_generic_sandbox(
    tool_name: str,
    strategy_endpoint: str,
    strategy_fields: Dict[str, str],
    expected_output: Optional[Dict[str, Any]] = None,
) -> SandboxResult:
    if not tool_registry.has(tool_name):
        return SandboxResult(executed=False, passed=False,
                             error=f"Unknown tool: {tool_name}")

    tool = tool_registry.get(tool_name)
    scenario = tool.active_scenario
    contract = scenario.contract
    expected_endpoint = contract.get("endpoint")

    if strategy_endpoint != expected_endpoint:
        return SandboxResult(executed=False, passed=False,
            error=f"Endpoint mismatch: {strategy_endpoint} vs {expected_endpoint}")

    expected_fields = _extract_field_keys(contract)
    for key, expected_value in expected_fields.items():
        if strategy_fields.get(key) != expected_value:
            return SandboxResult(executed=False, passed=False,
                error=f"Field mismatch on {key}: {strategy_fields.get(key)} vs {expected_value}")

    try:
        raw = scenario.simulate()
    except Exception as e:
        return SandboxResult(executed=True, passed=False, error=f"Simulator failed: {e}")

    output = {"tool": tool_name, "version": tool.active_version, "raw": raw}

    if expected_output:
        for key, val in expected_output.items():
            if raw.get(key) != val:
                return SandboxResult(executed=True, passed=False, output=output,
                    error=f"Output mismatch on '{key}': got {raw.get(key)} expected {val}")

    return SandboxResult(executed=True, passed=True, output=output)
