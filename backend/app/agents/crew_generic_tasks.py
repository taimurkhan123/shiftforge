"""
Generic CrewAI task builders for multi-tool adaptation.

Mirrors crew_tasks.py but replaces the weather-specific strategy task
with a dynamic one driven by the tool's contract.
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
    ValidationResult,
)
from app.models.generic import GenericStrategySpec


def make_generic_monitor_task(
    tool_name: str,
    expected_contract: dict,
    actual_response: dict | None,
    failure_reason: str | None,
) -> Task:
    return Task(
        description=(
            f"Tool: {tool_name}.\n\n"
            "Compare the expected contract to the actual tool response. "
            "Decide whether the environment changed.\n\n"
            f"Expected contract:\n{expected_contract}\n\n"
            f"Actual response:\n{actual_response}\n\n"
            f"Failure reason:\n{failure_reason}"
        ),
        expected_output=(
            'A JSON object with keys: status ("ok" or "change_detected"), '
            'severity ("low", "medium", "high"), reason (short string).'
        ),
        agent=monitor_agent,
        output_pydantic=MonitorResult,
    )


def make_generic_diagnosis_task(tool_name: str, old_contract: dict, new_contract: dict) -> Task:
    return Task(
        description=(
            f"Tool: {tool_name}.\n\n"
            "Compare the OLD contract to the NEW contract. Identify what changed.\n\n"
            f"Old contract:\n{old_contract}\n\n"
            f"New contract:\n{new_contract}"
        ),
        expected_output=(
            "A JSON object with keys: removed_fields (list), added_fields (list), "
            "endpoint_changed_from (string or null), endpoint_changed_to (string or null), "
            "summary (one sentence)."
        ),
        agent=diagnosis_agent,
        output_pydantic=DiagnosisResult,
    )


def make_generic_strategy_task(
    tool_name: str,
    new_contract: dict,
    diagnosis: DiagnosisResult,
    previous_strategy_version: str,
) -> Task:
    # Extract the *_field keys from the new contract so the LLM knows exactly
    # which field names to reuse in its strategy.
    field_keys = {k: v for k, v in new_contract.items() if k.endswith("_field")}
    return Task(
        description=(
            f"Tool: {tool_name}.\n\n"
            "Produce a new strategy that reaches the original task's goal through "
            "the changed environment. Use ONLY the field names that exist in the "
            "new contract. Return them in the 'fields' object.\n\n"
            f"New contract:\n{new_contract}\n\n"
            f"Required field keys (use these as keys in the 'fields' object):\n"
            f"{field_keys}\n\n"
            f"Diagnosis:\n{diagnosis.model_dump_json(indent=2)}\n\n"
            f"Previous strategy version: {previous_strategy_version}"
        ),
        expected_output=(
            "A JSON object with keys: version (string), endpoint (string), "
            "method (string, usually GET), fields (object mapping each required "
            "field key to its current field name), reasoning (short string)."
        ),
        agent=strategy_agent,
        output_pydantic=GenericStrategySpec,
    )


def make_generic_validation_task(
    tool_name: str,
    sandbox_result_json: str,
    original_task: str,
    expected_output: dict | None,
) -> Task:
    return Task(
        description=(
            f"Tool: {tool_name}.\n\n"
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
