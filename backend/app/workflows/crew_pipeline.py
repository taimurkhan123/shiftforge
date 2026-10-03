import os
"""
CrewAI adaptation pipeline.

Orchestrates 4 reasoning agents (Monitor, Diagnosis, Strategy, Validation) via
a CrewAI Crew, with 2 deterministic steps (Sandbox, Recovery) running between
Crew tasks.

Each Crew task emits an SSE event so the frontend can animate the workflow.
"""

import time
import uuid


# Disable CrewAI telemetry/tracing at import time
os.environ["CREWAI_TRACING_ENABLED"] = "false"
os.environ["CREWAI_TELEMETRY_OPT_OUT"] = "true"

from crewai import Crew, Process

from app.models.run import RunStatus, RunStep
from app.models.adaptation import StrategySpec
from app.sandbox.environment import environment_registry
from app.services.events import event_bus
from app.services import repository
from app.agents.crew_tasks import (
    make_monitor_task,
    make_diagnosis_task,
    make_strategy_task,
    make_validation_task,
)
from app.agents.sandbox import run_sandbox
from app.agents.recovery import run_recovery, RecoveryError


EXPECTED_OUTPUT = {"temperature": 28.0, "condition": "Sunny"}


async def _emit(run_id, stage, status, message, data=None, final=False):
    payload = {
        "stage": stage,
        "status": status,
        "message": message,
        "data": {**(data or {}), "final": final},
    }
    await event_bus.publish(run_id, payload)


def _run_crew_sync(crew: Crew):
    """Run the crew synchronously (CrewAI is sync-first)."""
    return crew.kickoff()


async def run_crew_pipeline(run, original_strategy, failure_reason, actual_response):
    """
    Orchestrate adaptation through a CrewAI Crew.
    Mutates `run` in place and returns it.
    """
    started = time.perf_counter()

    def add_step(stage, status, message, data=None):
        elapsed = int((time.perf_counter() - started) * 1000)
        step = RunStep(
            stage=stage, status=status, message=message,
            duration_ms=elapsed, data=data or {},
        )
        run.steps.append(step)
        return step

    old_contract = environment_registry.get("v1").model_dump()
    new_contract = environment_registry.active_contract.model_dump()

    # ---------- 1. MONITOR ----------
    run.status = RunStatus.CHANGE_DETECTED
    await _emit(run.run_id, "change_detected", "warning",
                "Environment change detected. Starting CrewAI adaptation pipeline.")

    try:
        monitor_task = make_monitor_task(old_contract, actual_response, failure_reason)
        monitor_crew = Crew(
            agents=[monitor_task.agent],
            tasks=[monitor_task],
            process=Process.sequential,
            verbose=False,
            tracing=False,
        )
        monitor_result_raw = _run_crew_sync(monitor_crew)

        # CrewAI returns the pydantic instance via .pydantic on task output,
        # or we can access it from tasks[0].output.pydantic after kickoff
        monitor_result = monitor_task.output.pydantic

        add_step("monitor", "success",
                 "Monitor: " + monitor_result.status + " (" + monitor_result.severity + ") - " + monitor_result.reason,
                 data=monitor_result.model_dump())
        await _emit(run.run_id, "change_detected", "success",
                    "Monitor confirmed: " + monitor_result.reason,
                    data=monitor_result.model_dump())
    except Exception as e:
        add_step("monitor", "failed", "Monitor agent failed: " + str(e))
        await _emit(run.run_id, "change_detected", "failed",
                    "Monitor agent failed: " + str(e), final=True)
        run.status = RunStatus.FAILED
        repository.save_run(run)
        return run

    # ---------- 2. DIAGNOSIS ----------
    run.status = RunStatus.DIAGNOSING
    await _emit(run.run_id, "diagnosis", "running", "Diagnosing the change...")

    try:
        diagnosis_task = make_diagnosis_task(old_contract, new_contract)
        diagnosis_crew = Crew(
            agents=[diagnosis_task.agent],
            tasks=[diagnosis_task],
            process=Process.sequential,
            verbose=False,
            tracing=False,
        )
        _run_crew_sync(diagnosis_crew)
        diagnosis_result = diagnosis_task.output.pydantic

        add_step("diagnosis", "success",
                 "Diagnosis: " + diagnosis_result.summary,
                 data=diagnosis_result.model_dump())
        await _emit(run.run_id, "diagnosis", "success",
                    "Diagnosis: " + diagnosis_result.summary,
                    data=diagnosis_result.model_dump())
    except Exception as e:
        add_step("diagnosis", "failed", "Diagnosis agent failed: " + str(e))
        await _emit(run.run_id, "diagnosis", "failed",
                    "Diagnosis agent failed: " + str(e), final=True)
        run.status = RunStatus.FAILED
        repository.save_run(run)
        return run

    # ---------- 3. STRATEGY ----------
    run.status = RunStatus.STRATEGIZING
    await _emit(run.run_id, "strategy", "running", "Generating new strategy...")

    try:
        strategy_task = make_strategy_task(
            new_contract, diagnosis_result, original_strategy.version
        )
        strategy_crew = Crew(
            agents=[strategy_task.agent],
            tasks=[strategy_task],
            process=Process.sequential,
            verbose=False,
            tracing=False,
        )
        _run_crew_sync(strategy_crew)
        strategy_result = strategy_task.output.pydantic

        add_step("strategy", "success",
                 "New strategy: " + strategy_result.version + " - " + strategy_result.method + " " + strategy_result.endpoint,
                 data=strategy_result.model_dump())
        await _emit(run.run_id, "strategy", "success",
                    "New strategy: " + strategy_result.version + " - " + strategy_result.method + " " + strategy_result.endpoint,
                    data=strategy_result.model_dump())
    except Exception as e:
        add_step("strategy", "failed", "Strategy agent failed: " + str(e))
        await _emit(run.run_id, "strategy", "failed",
                    "Strategy agent failed: " + str(e), final=True)
        run.status = RunStatus.FAILED
        repository.save_run(run)
        return run

    # ---------- 4. SANDBOX (deterministic — no LLM) ----------
    run.status = RunStatus.SANDBOXING
    await _emit(run.run_id, "sandbox", "running",
                "Testing " + strategy_result.version + " in sandbox...")

    sandbox_result = run_sandbox(strategy_result, new_contract, EXPECTED_OUTPUT)
    if sandbox_result.passed:
        add_step("sandbox", "success",
                 "Sandbox passed: " + str(sandbox_result.output),
                 data=sandbox_result.model_dump())
        await _emit(run.run_id, "sandbox", "success",
                    "Sandbox passed: " + str(sandbox_result.output),
                    data=sandbox_result.model_dump())
    else:
        add_step("sandbox", "failed",
                 "Sandbox failed: " + str(sandbox_result.error),
                 data=sandbox_result.model_dump())
        await _emit(run.run_id, "sandbox", "failed",
                    "Sandbox failed: " + str(sandbox_result.error),
                    data=sandbox_result.model_dump(), final=True)
        run.status = RunStatus.FAILED
        repository.save_run(run)
        repository.save_adaptation(
            adaptation_id="AD-" + uuid.uuid4().hex[:6].upper(),
            run_id=run.run_id,
            change_type="endpoint+field_rename",
            from_strategy=original_strategy.version,
            to_strategy=strategy_result.version,
            result="failed",
            detail={"sandbox": sandbox_result.model_dump()},
        )
        return run

    # ---------- 5. VALIDATION (CrewAI) ----------
    run.status = RunStatus.VALIDATING
    await _emit(run.run_id, "validation", "running", "Validating sandbox result...")

    try:
        validation_task = make_validation_task(
            sandbox_result.model_dump_json(indent=2),
            run.task,
            EXPECTED_OUTPUT,
        )
        validation_crew = Crew(
            agents=[validation_task.agent],
            tasks=[validation_task],
            process=Process.sequential,
            verbose=False,
            tracing=False,
        )
        _run_crew_sync(validation_crew)
        validation_result = validation_task.output.pydantic

        vstatus = "success" if validation_result.validated else "failed"
        vmsg = "Validation: " + validation_result.reason + " (confidence " + str(round(validation_result.confidence, 2)) + ")"
        add_step("validation", vstatus, vmsg, data=validation_result.model_dump())
        await _emit(run.run_id, "validation", vstatus, vmsg,
                    data=validation_result.model_dump())

        if not validation_result.validated:
            run.status = RunStatus.FAILED
            await _emit(run.run_id, "validation", "failed",
                        "Strategy rejected by validator.", final=True)
            repository.save_run(run)
            return run
    except Exception as e:
        add_step("validation", "failed", "Validation agent failed: " + str(e))
        await _emit(run.run_id, "validation", "failed",
                    "Validation agent failed: " + str(e), final=True)
        run.status = RunStatus.FAILED
        repository.save_run(run)
        return run

    # ---------- 6. RECOVERY (deterministic) ----------
    run.status = RunStatus.RECOVERING
    await _emit(run.run_id, "recovery", "running",
                "Adopting new strategy and retrying original task...")

    try:
        recovery_result = run_recovery(strategy_result, validation_result)
        add_step("recovery", "success",
                 "Recovery succeeded: " + str(recovery_result),
                 data=recovery_result)
        await _emit(run.run_id, "recovery", "success",
                    "Recovery succeeded: " + str(recovery_result),
                    data=recovery_result)
    except RecoveryError as e:
        add_step("recovery", "failed", "Recovery failed: " + str(e))
        await _emit(run.run_id, "recovery", "failed",
                    "Recovery failed: " + str(e), final=True)
        run.status = RunStatus.FAILED
        repository.save_run(run)
        return run

    # ---------- COMPLETE ----------
    run.status = RunStatus.SUCCESS
    run.final_strategy_version = strategy_result.version
    run.result = {
        "temperature": recovery_result["temperature"],
        "condition": recovery_result["condition"],
    }
    run.total_adaptation_ms = int((time.perf_counter() - started) * 1000)

    add_step("complete", "success",
             "Original task completed with adapted strategy.")

    repository.save_strategy(
        version=strategy_result.version,
        endpoint=strategy_result.endpoint,
        method=strategy_result.method,
        temperature_field=strategy_result.temperature_field,
        condition_field=strategy_result.condition_field,
        reasoning=strategy_result.reasoning,
    )
    repository.save_adaptation(
        adaptation_id="AD-" + uuid.uuid4().hex[:6].upper(),
        run_id=run.run_id,
        change_type="endpoint+field_rename",
        from_strategy=original_strategy.version,
        to_strategy=strategy_result.version,
        result="success",
        detail={
            "diagnosis": diagnosis_result.model_dump(),
            "strategy": strategy_result.model_dump(),
            "validation": validation_result.model_dump(),
        },
    )
    repository.save_run(run)

    await _emit(run.run_id, "complete", "success",
                "Original task completed with adapted strategy.",
                data={
                    "result": run.result,
                    "strategy": strategy_result.model_dump(),
                    "diagnosis": diagnosis_result.model_dump(),
                },
                final=True)
    return run
