"""
Tool-agnostic CrewAI adaptation pipeline.

Runs the same 4 reasoning agents as crew_pipeline.py, but works for any
registered tool. Uses the generic sandbox and recovery helpers so no
weather-specific logic leaks into the multi-tool path.
"""

import os
os.environ["CREWAI_TRACING_ENABLED"] = "false"
os.environ["CREWAI_TELEMETRY_OPT_OUT"] = "true"

import time
import uuid

from crewai import Crew, Process

from app.models.run import RunStatus, RunStep
from app.services.events import event_bus
from app.services import repository
from app.tools.registry import tool_registry
from app.agents.crew_generic_tasks import (
    make_generic_monitor_task,
    make_generic_diagnosis_task,
    make_generic_strategy_task,
    make_generic_validation_task,
)
from app.agents.sandbox_generic import run_generic_sandbox
from app.agents.recovery_generic import run_generic_recovery, GenericRecoveryError


async def _emit(run_id, stage, status, message, data=None, final=False):
    await event_bus.publish(run_id, {
        "stage": stage,
        "status": status,
        "message": message,
        "data": {**(data or {}), "final": final},
    })


def _run_crew_sync(crew, max_retries=2):
    import time as _time
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            return crew.kickoff()
        except Exception as e:
            msg = str(e)
            last_error = e
            if "tool choice" in msg.lower() or "tool_use_failed" in msg.lower():
                if attempt < max_retries:
                    _time.sleep(1.5)
                    continue
            raise
    raise last_error


async def run_tool_pipeline(run, tool_name, task, failure_reason, actual_response):
    """
    Tool-agnostic adaptation pipeline.
    run: RunState
    tool_name: name of registered tool
    task: user-provided task string
    failure_reason: reason original strategy failed
    actual_response: raw response that triggered the failure
    """
    started = time.perf_counter()

    def add_step(stage, status, message, data=None):
        elapsed = int((time.perf_counter() - started) * 1000)
        step = RunStep(stage=stage, status=status, message=message,
                       duration_ms=elapsed, data=data or {})
        run.steps.append(step)
        return step

    tool = tool_registry.get(tool_name)
    old_contract = tool.get_scenario("v1").contract
    new_contract = tool.active_scenario.contract

    # 1. MONITOR
    run.status = RunStatus.CHANGE_DETECTED
    await _emit(run.run_id, "change_detected", "warning",
                f"Environment change detected for tool '{tool_name}'. Starting adaptation.")
    try:
        monitor_task = make_generic_monitor_task(tool_name, old_contract, actual_response, failure_reason)
        crew = Crew(agents=[monitor_task.agent], tasks=[monitor_task],
                    process=Process.sequential, verbose=False, tracing=False)
        _run_crew_sync(crew)
        monitor_result = monitor_task.output.pydantic
        add_step("monitor", "success",
                 f"Monitor: {monitor_result.status} ({monitor_result.severity}) - {monitor_result.reason}",
                 data=monitor_result.model_dump())
        await _emit(run.run_id, "change_detected", "success",
                    f"Monitor confirmed: {monitor_result.reason}",
                    data=monitor_result.model_dump())
    except Exception as e:
        add_step("monitor", "failed", f"Monitor agent failed: {e}")
        await _emit(run.run_id, "change_detected", "failed", f"Monitor agent failed: {e}", final=True)
        run.status = RunStatus.FAILED
        repository.save_run(run)
        return run

    # 2. DIAGNOSIS
    run.status = RunStatus.DIAGNOSING
    await _emit(run.run_id, "diagnosis", "running", "Diagnosing the change...")
    try:
        diag_task = make_generic_diagnosis_task(tool_name, old_contract, new_contract)
        crew = Crew(agents=[diag_task.agent], tasks=[diag_task],
                    process=Process.sequential, verbose=False, tracing=False)
        _run_crew_sync(crew)
        diagnosis = diag_task.output.pydantic
        add_step("diagnosis", "success", f"Diagnosis: {diagnosis.summary}", data=diagnosis.model_dump())
        await _emit(run.run_id, "diagnosis", "success", f"Diagnosis: {diagnosis.summary}",
                    data=diagnosis.model_dump())
    except Exception as e:
        add_step("diagnosis", "failed", f"Diagnosis agent failed: {e}")
        await _emit(run.run_id, "diagnosis", "failed", f"Diagnosis agent failed: {e}", final=True)
        run.status = RunStatus.FAILED
        repository.save_run(run)
        return run

    # 3. STRATEGY
    run.status = RunStatus.STRATEGIZING
    await _emit(run.run_id, "strategy", "running", "Generating new strategy...")
    try:
        strat_task = make_generic_strategy_task(tool_name, new_contract, diagnosis, "v1")
        crew = Crew(agents=[strat_task.agent], tasks=[strat_task],
                    process=Process.sequential, verbose=False, tracing=False)
        _run_crew_sync(crew)
        strategy = strat_task.output.pydantic
        add_step("strategy", "success",
                 f"New strategy: {strategy.version} - {strategy.method} {strategy.endpoint}",
                 data=strategy.model_dump())
        await _emit(run.run_id, "strategy", "success",
                    f"New strategy: {strategy.version} - {strategy.method} {strategy.endpoint}",
                    data=strategy.model_dump())
    except Exception as e:
        add_step("strategy", "failed", f"Strategy agent failed: {e}")
        await _emit(run.run_id, "strategy", "failed", f"Strategy agent failed: {e}", final=True)
        run.status = RunStatus.FAILED
        repository.save_run(run)
        return run

    # 4. SANDBOX (deterministic)
    run.status = RunStatus.SANDBOXING
    await _emit(run.run_id, "sandbox", "running", f"Testing {strategy.version} in sandbox...")
    sandbox_result = run_generic_sandbox(tool_name, strategy.endpoint, strategy.fields)
    if sandbox_result.passed:
        add_step("sandbox", "success", f"Sandbox passed: {sandbox_result.output}",
                 data=sandbox_result.model_dump())
        await _emit(run.run_id, "sandbox", "success", f"Sandbox passed: {sandbox_result.output}",
                    data=sandbox_result.model_dump())
    else:
        add_step("sandbox", "failed", f"Sandbox failed: {sandbox_result.error}",
                 data=sandbox_result.model_dump())
        await _emit(run.run_id, "sandbox", "failed", f"Sandbox failed: {sandbox_result.error}",
                    data=sandbox_result.model_dump(), final=True)
        run.status = RunStatus.FAILED
        repository.save_run(run)
        return run

    # 5. VALIDATION
    run.status = RunStatus.VALIDATING
    await _emit(run.run_id, "validation", "running", "Validating sandbox result...")
    try:
        val_task = make_generic_validation_task(tool_name, sandbox_result.model_dump_json(indent=2),
                                                task, None)
        crew = Crew(agents=[val_task.agent], tasks=[val_task],
                    process=Process.sequential, verbose=False, tracing=False)
        _run_crew_sync(crew)
        validation = val_task.output.pydantic
        vstatus = "success" if validation.validated else "failed"
        add_step("validation", vstatus,
                 f"Validation: {validation.reason} (confidence {round(validation.confidence, 2)})",
                 data=validation.model_dump())
        await _emit(run.run_id, "validation", vstatus,
                    f"Validation: {validation.reason} (confidence {round(validation.confidence, 2)})",
                    data=validation.model_dump())
        if not validation.validated:
            run.status = RunStatus.FAILED
            await _emit(run.run_id, "validation", "failed", "Strategy rejected by validator.", final=True)
            repository.save_run(run)
            return run
    except Exception as e:
        add_step("validation", "failed", f"Validation agent failed: {e}")
        await _emit(run.run_id, "validation", "failed", f"Validation agent failed: {e}", final=True)
        run.status = RunStatus.FAILED
        repository.save_run(run)
        return run

    # 6. RECOVERY
    run.status = RunStatus.RECOVERING
    await _emit(run.run_id, "recovery", "running", "Adopting new strategy and retrying task...")
    try:
        result = run_generic_recovery(tool_name, strategy.endpoint, strategy.fields, validation)
        add_step("recovery", "success", f"Recovery succeeded: {result}", data=result)
        await _emit(run.run_id, "recovery", "success", f"Recovery succeeded: {result}", data=result)
    except GenericRecoveryError as e:
        add_step("recovery", "failed", f"Recovery failed: {e}")
        await _emit(run.run_id, "recovery", "failed", f"Recovery failed: {e}", final=True)
        run.status = RunStatus.FAILED
        repository.save_run(run)
        return run

    # COMPLETE
    run.status = RunStatus.SUCCESS
    run.final_strategy_version = strategy.version
    run.result = result.get("raw", {})
    run.total_adaptation_ms = int((time.perf_counter() - started) * 1000)

    add_step("complete", "success", "Original task completed with adapted strategy.")
    repository.save_run(run)

    await _emit(run.run_id, "complete", "success",
                "Original task completed with adapted strategy.",
                data={"result": run.result, "strategy": strategy.model_dump(),
                      "diagnosis": diagnosis.model_dump()},
                final=True)
    return run
