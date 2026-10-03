from app.services.executor import execute_strategy, StrategyExecutionError


class RecoveryError(Exception):
    pass


def run_recovery(strategy, validation):
    if not validation.validated:
        raise RecoveryError("Refusing to recover: strategy not validated.")
    try:
        result = execute_strategy(strategy)
    except StrategyExecutionError as e:
        raise RecoveryError("Recovery execution failed: " + e.message)
    return {
        "temperature": result.temperature,
        "condition": result.condition,
        "raw": result.raw,
    }
