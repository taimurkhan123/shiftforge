import time
import uuid

from app.models.run import RunStatus, RunStep
from app.sandbox.environment import environment_registry
from app.services.events import event_bus
from app.services import repository
from app.agents.monitor import run_monitor
from app.agents.diagnosis import run_diagnosis
from app.agents.strategy import run_strategy
from app.agents.sandbox import run_sandbox
from app.agents.validation import run_validation
from app.agents.recovery import run_recovery, RecoveryError


EXPECTED_OUTPUT = {"temperature": 28.0, "condition": "Sunny"}


async def _emit(run_id, stage, status, message, data=None, final=False):
    payload = {"stage": stage, "status": status, "message": message,
               "data": {**(data or {}), "final": final}}
    await event_bus.publish(run_id, payload)


async def run_adaptation_pipeline(run, original_strategy, failure_reason, actual_response):
    started = time.perf_counter()

    def add_step(stage, status, message, data=None):
        elapsed = int((time.perf_counter() - started) * 1000)
        step = RunStep(stage=stage, status=status, message=message,
                       duration_ms=elapsed, data=data or {})
        run.steps.append(step)
        return step

    old_contract = environment_registry.get("v1").model_dump()
    new_contract = environment_registry.active_contract.model_dump()

    # 1. MONITOR
    run.status = RunStatus.CHANGE_DETECTED
    await _emit(run.run_id, "change_detected", "warning",
                "Environment change detected. Starting adaptation pipeline.")
    try:
        monitor = run_monitor(old_contract, actual_response, failure_reason)
        add_step("monitor", "success",
                 "Monitor: " + monitor.status + " (" + monitor.severity + ") - " + monitor.reason,
                 data=monitor.model_dump())
        await _emit(run.run_id, "change_detected", "success",
                    "Monitor confirmed: " + monitor.reason,
                    data=monitor.model_dump())
    except Exception as e:
        add_step("monitor", "failed", "Monitor failed: " + str(e))
        await _emit(run.run_id, "change_detected", "failed",
                    "Monitor failed: " + str(e), final=True)
        run.status = RunStatus.FAILED
        repository.save_run(run)
        return run

    # 2. DIAGNOSIS
    run.status = RunStatus.DIAGNOSING
    await _emit(run.run_id, "diagnosis", "running", "Diagnosing...")
    try:
        diagnosis = run_diagnosis(old_contract, new_contract)
        add_step("diagnosis", "success", "Diagnosis: " + diagnosis.summary,
                 data=diagnosis.model_dump())
        await _emit(run.run_id, "diagnosis", "success",
                    "Diagnosis: " + diagnosis.summary,
                    data=diagnosis.model_dump())
    except Exception as e:
        add_step("diagnosis", "failed", "Diagnosis failed: " + str(e))
        await _emit(run.run_id, "diagnosis", "failed",
                    "Diagnosis failed: " + str(e), final=True)
        run.status = RunStatus.FAILED
        repository.save_run(run)
        return run

    # 3. STRATEGY
    run.status = RunStatus.STRATEGIZING
    await _emit(run.run_id, "strategy", "running", "Generating strategy...")
    try:
        strategy = run_strategy(new_contract, diagnosis,
                                previous_strategy_version=original_strategy.version)
        add_step("strategy", "success",
                 "New strategy: " + strategy.version + " - " + strategy.method + " " + strategy.endpoint,
                 data=strategy.model_dump())
        await _emit(run.run_id, "strategy", "success",
                    "New strategy: " + strategy.version + " - " + strategy.method + " " + strategy.endpoint,
                    data=strategy.model_dump())
    except Exception as e:
        add_step("strategy", "failed", "Strategy failed: " + str(e))
        await _emit(run.run_id, "strategy", "failed",
                    "Strategy failed: " + str(e), final=True)
        run.status = RunStatus.FAILED
        repository.save_run(run)
        return run

    # 4. SANDBOX
    run.status = RunStatus.SANDBOXING
    await _emit(run.run_id, "sandbox", "running",
                "Testing " + strategy.version + " in sandbox...")
    sandbox_result = run_sandbox(strategy, new_contract, EXPECTED_OUTPUT)
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
            to_strategy=strategy.version,
            result="failed",
            detail={"sandbox": sandbox_result.model_dump()},
        )
        return run

    # 5. VALIDATION
    run.status = RunStatus.VALIDATING
    await _emit(run.run_id, "validation", "running", "Validating...")
    try:
        validation = run_validation(sandbox_result, run.task, EXPECTED_OUTPUT)
        vstatus = "success" if validation.validated else "failed"
        vmsg = "Validation: " + validation.reason + " (confidence " + str(round(validation.confidence, 2)) + ")"
        add_step("validation", vstatus, vmsg, data=validation.model_dump())
        await _emit(run.run_id, "validation", vstatus, vmsg,
                    data=validation.model_dump())
        if not validation.validated:
            run.status = RunStatus.FAILED
            await _emit(run.run_id, "validation", "failed",
                        "Strategy rejected.", final=True)
            repository.save_run(run)
            return run
    except Exception as e:
        add_step("validation", "failed", "Validation failed: " + str(e))
        await _emit(run.run_id, "validation", "failed",
                    "Validation failed: " + str(e), final=True)
        run.status = RunStatus.FAILED
        repository.save_run(run)
        return run

    # 6. RECOVERY
    run.status = RunStatus.RECOVERING
    await _emit(run.run_id, "recovery", "running",
                "Adopting new strategy and retrying task...")
    try:
        result = run_recovery(strategy, validation)
        add_step("recovery", "success", "Recovery succeeded: " + str(result), data=result)
        await _emit(run.run_id, "recovery", "success",
                    "Recovery succeeded: " + str(result), data=result)
    except RecoveryError as e:
        add_step("recovery", "failed", "Recovery failed: " + str(e))
        await _emit(run.run_id, "recovery", "failed",
                    "Recovery failed: " + str(e), final=True)
        run.status = RunStatus.FAILED
        repository.save_run(run)
        return run

    # COMPLETE
    run.status = RunStatus.SUCCESS
    run.final_strategy_version = strategy.version
    run.result = {"temperature": result["temperature"], "condition": result["condition"]}
    run.total_adaptation_ms = int((time.perf_counter() - started) * 1000)

    add_step("complete", "success", "Original task completed with adapted strategy.")

    repository.save_strategy(
        version=strategy.version,
        endpoint=strategy.endpoint,
        method=strategy.method,
        temperature_field=strategy.temperature_field,
        condition_field=strategy.condition_field,
        reasoning=strategy.reasoning,
    )
    repository.save_adaptation(
        adaptation_id="AD-" + uuid.uuid4().hex[:6].upper(),
        run_id=run.run_id,
        change_type="endpoint+field_rename",
        from_strategy=original_strategy.version,
        to_strategy=strategy.version,
        result="success",
        detail={
            "diagnosis": diagnosis.model_dump(),
            "strategy": strategy.model_dump(),
            "validation": validation.model_dump(),
        },
    )
    repository.save_run(run)

    await _emit(run.run_id, "complete", "success",
                "Original task completed with adapted strategy.",
                data={"result": run.result,
                      "strategy": strategy.model_dump(),
                      "diagnosis": diagnosis.model_dump()},
                final=True)
    return run
