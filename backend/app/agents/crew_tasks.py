"""
CrewAI Task builders.

Each function constructs a Task for a specific agent, given the runtime inputs
for one adaptation run. Tasks are built fresh per run so they always see the
latest environment state.
"""

from crewai import Task
from app.agents.crew_agents import (
    monitor_agent,
    diagnosis_agent,
    strategy_agent,
    validation_agent,
)
from app.models.adaptation import (
    MonitorResult,
    DiagnosisResult,
    StrategySpec,
    ValidationResult,
)


def make_monitor_task(
    expected_contract: dict,
    actual_response: dict | None,
    failure_reason: str | None,
) -> Task:
    return Task(
        description=(
            "Compare the expected contract to the actual tool response. "
            "Decide whether the environment changed.\n\n"
            f"Expected contract:\n{expected_contract}\n\n"
            f"Actual response:\n{actual_response}\n\n"
            f"Failure reason reported by the executor:\n{failure_reason}"
        ),
        expected_output=(
            "A JSON object with keys: status (\"ok\" or \"change_detected\"), "
            "severity (\"low\", \"medium\", or \"high\"), and reason (a short string)."
        ),
        agent=monitor_agent,
        output_pydantic=MonitorResult,
    )


def make_diagnosis_task(old_contract: dict, new_contract: dict) -> Task:
    return Task(
        description=(
            "Compare the OLD contract to the NEW contract. Identify exactly what "
            "changed: removed fields, added fields, and any endpoint change.\n\n"
            f"Old contract:\n{old_contract}\n\n"
            f"New contract:\n{new_contract}"
        ),
        expected_output=(
            "A JSON object with keys: removed_fields (list of strings), "
            "added_fields (list of strings), endpoint_changed_from (string or null), "
            "endpoint_changed_to (string or null), summary (one-sentence string)."
        ),
        agent=diagnosis_agent,
        output_pydantic=DiagnosisResult,
    )


def make_strategy_task(
    new_contract: dict,
    diagnosis: DiagnosisResult,
    previous_strategy_version: str,
) -> Task:
    return Task(
        description=(
            "Produce a new strategy that reaches the original task's goal through "
            "the changed environment. Use only field names that exist in the new "
            "contract. Increase the version number from the previous strategy.\n\n"
            f"New contract:\n{new_contract}\n\n"
            f"Diagnosis:\n{diagnosis.model_dump_json(indent=2)}\n\n"
            f"Previous strategy version: {previous_strategy_version}"
        ),
        expected_output=(
            "A JSON object with keys: version (string), endpoint (string), "
            "method (string, usually \"GET\"), temperature_field (string), "
            "condition_field (string), reasoning (short string)."
        ),
        agent=strategy_agent,
        output_pydantic=StrategySpec,
    )


def make_validation_task(
    sandbox_result_json: str,
    original_task: str,
    expected_output: dict | None,
) -> Task:
    return Task(
        description=(
            "Given the sandbox result and the original task, decide whether the "
            "strategy is safe to adopt. If the sandbox did not execute or did not "
            "pass, validated MUST be false.\n\n"
            f"Original task: {original_task}\n\n"
            f"Sandbox result:\n{sandbox_result_json}\n\n"
            f"Expected output:\n{expected_output}"
        ),
        expected_output=(
            "A JSON object with keys: validated (boolean), "
            "confidence (number between 0 and 1), reason (short string)."
        ),
        agent=validation_agent,
        output_pydantic=ValidationResult,
    )
