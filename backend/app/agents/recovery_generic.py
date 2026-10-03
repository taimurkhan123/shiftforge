"""
Generic recovery — adopts a validated strategy and re-executes the tool call.

No hardcoded weather logic.
"""

from typing import Dict, Any
from app.models.adaptation import ValidationResult
from app.services.executor_generic import execute_generic_strategy, GenericStrategyError


class GenericRecoveryError(Exception):
    pass


def run_generic_recovery(
    tool_name: str,
    strategy_endpoint: str,
    strategy_fields: Dict[str, str],
    validation: ValidationResult,
) -> Dict[str, Any]:
    if not validation.validated:
        raise GenericRecoveryError(f"Refusing to recover: {validation.reason}")

    try:
        result = execute_generic_strategy(tool_name, strategy_endpoint, strategy_fields)
    except GenericStrategyError as e:
        raise GenericRecoveryError(f"Recovery execution failed: {e.message}")

    return result
