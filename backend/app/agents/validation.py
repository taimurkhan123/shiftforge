from app.agents.llm import call_llm_json
from app.models.adaptation import SandboxResult, ValidationResult

SYSTEM = """You are the Validation Agent in ShiftForge.
Given a sandbox result and the original task, decide whether the strategy is safe to adopt.

Return ONLY a JSON object with these keys:
- validated: boolean
- confidence: number between 0 and 1
- reason: one short sentence

Rules:
- If sandbox did not execute OR did not pass, validated MUST be false.
- If sandbox passed, validated true with confidence >= 0.85.
"""


def run_validation(sandbox_result, original_task, expected_output):
    user = "Original task: " + original_task
    user += "\n\nSandbox result:\n" + sandbox_result.model_dump_json(indent=2)
    user += "\n\nExpected output:\n" + str(expected_output)
    return call_llm_json(SYSTEM, user, ValidationResult)
