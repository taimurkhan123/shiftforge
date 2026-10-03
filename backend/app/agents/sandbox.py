from app.models.adaptation import SandboxResult
from app.sandbox.tools import call_tool


def run_sandbox(strategy, target_contract, expected_output=None):
    expected_endpoint = target_contract.get("endpoint")
    expected_temp_field = target_contract.get("temperature_field")
    expected_cond_field = target_contract.get("condition_field")

    if strategy.endpoint != expected_endpoint:
        return SandboxResult(executed=False, passed=False,
            error="Endpoint mismatch: " + str(strategy.endpoint) + " vs " + str(expected_endpoint))
    if strategy.temperature_field != expected_temp_field:
        return SandboxResult(executed=False, passed=False,
            error="temperature_field mismatch: " + str(strategy.temperature_field) + " vs " + str(expected_temp_field))
    if strategy.condition_field != expected_cond_field:
        return SandboxResult(executed=False, passed=False,
            error="condition_field mismatch: " + str(strategy.condition_field) + " vs " + str(expected_cond_field))

    version = target_contract.get("version")
    tool_name = {"v1": "fetch_weather_v1", "v2": "fetch_weather_v2"}.get(version)
    if not tool_name:
        return SandboxResult(executed=False, passed=False,
            error="No sandbox tool for version " + str(version))

    try:
        raw = call_tool(tool_name)
    except Exception as e:
        return SandboxResult(executed=True, passed=False, error="Tool raised: " + str(e))

    try:
        temperature = float(raw[strategy.temperature_field])
        condition = str(raw[strategy.condition_field])
    except (KeyError, TypeError, ValueError) as e:
        return SandboxResult(executed=True, passed=False, error="Fields missing: " + str(e))

    output = {"temperature": temperature, "condition": condition}

    if expected_output:
        for key, val in expected_output.items():
            if output.get(key) != val:
                return SandboxResult(executed=True, passed=False, output=output,
                    error="Mismatch on " + key)

    return SandboxResult(executed=True, passed=True, output=output)
