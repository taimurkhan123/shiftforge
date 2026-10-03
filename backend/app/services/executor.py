"""
Executes a StrategySpec against the CURRENT live environment.

The executor NEVER trusts the LLM. It only:
1. Reads the active contract from the environment registry.
2. Verifies the strategy's endpoint + fields match the active contract.
3. Calls a registered tool by name.
4. Normalizes the response into ToolResponse.
"""

from typing import Dict, Any
from app.models.contract import ToolContract, ToolResponse, ContractMismatch
from app.models.adaptation import StrategySpec
from app.sandbox.tools import call_tool
from app.sandbox.environment import environment_registry


class StrategyExecutionError(Exception):
    """Wraps ContractMismatch with more context for the timeline."""
    def __init__(self, message: str, tool_payload: Dict[str, Any] | None = None):
        super().__init__(message)
        self.message = message
        self.tool_payload = tool_payload or {}


def _tool_name_for_contract(contract: ToolContract) -> str:
    """Map an active contract to the tool that serves it."""
    if contract.version == "v1":
        return "fetch_weather_v1"
    if contract.version == "v2":
        return "fetch_weather_v2"
    raise StrategyExecutionError(f"No tool registered for contract {contract.version}")


def execute_strategy(strategy: StrategySpec) -> ToolResponse:
    """
    Run a strategy against the live environment.
    Raises StrategyExecutionError if the strategy doesn't match the active contract.
    """
    active: ToolContract = environment_registry.active_contract

    # Strict contract check — the strategy MUST match what the env currently offers
    if strategy.endpoint != active.endpoint:
        raise StrategyExecutionError(
            f"Endpoint mismatch: strategy expects '{strategy.endpoint}' "
            f"but environment offers '{active.endpoint}'.",
            tool_payload={"expected": strategy.endpoint, "actual": active.endpoint},
        )

    if strategy.temperature_field != active.temperature_field:
        raise StrategyExecutionError(
            f"Field mismatch: strategy reads '{strategy.temperature_field}' "
            f"but environment exposes '{active.temperature_field}'.",
            tool_payload={
                "expected_field": strategy.temperature_field,
                "actual_field": active.temperature_field,
            },
        )

    if strategy.condition_field != active.condition_field:
        raise StrategyExecutionError(
            f"Field mismatch: strategy reads '{strategy.condition_field}' "
            f"but environment exposes '{active.condition_field}'.",
            tool_payload={
                "expected_field": strategy.condition_field,
                "actual_field": active.condition_field,
            },
        )

    # Execute the registered tool
    tool_name = _tool_name_for_contract(active)
    try:
        raw = call_tool(tool_name)
    except ContractMismatch as e:
        raise StrategyExecutionError(e.reason, tool_payload=e.payload)

    # Normalize using the active contract's field names
    try:
        temperature = float(raw[active.temperature_field])
        condition = str(raw[active.condition_field])
    except (KeyError, TypeError, ValueError) as e:
        raise StrategyExecutionError(
            f"Response did not contain expected fields: {e}",
            tool_payload=raw,
        )

    return ToolResponse(temperature=temperature, condition=condition, raw=raw)