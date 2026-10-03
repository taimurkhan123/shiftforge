from app.agents.llm import call_llm_json
from app.models.adaptation import MonitorResult

SYSTEM = """You are the Monitor Agent in ShiftForge.
Given an expected API contract and an actual tool response, decide whether the environment has changed.

Return ONLY a JSON object with these keys:
- status: "ok" or "change_detected"
- severity: "low", "medium", or "high"
- reason: a short explanation

Rules:
- If every expected field is present and endpoint matches, return status "ok".
- If any field is missing/renamed or endpoint changed, return status "change_detected".
"""


def run_monitor(expected_contract, actual_response, failure_reason):
    user = "Expected contract:\n" + str(expected_contract)
    user += "\n\nActual response:\n" + str(actual_response)
    user += "\n\nFailure reason:\n" + str(failure_reason)
    return call_llm_json(SYSTEM, user, MonitorResult)
