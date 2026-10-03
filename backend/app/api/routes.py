import json
import time
import uuid
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.sandbox.environment import environment_registry
from app.services.events import event_bus
from app.services.executor import execute_strategy, StrategyExecutionError
from app.services import repository
from app.models.adaptation import StrategySpec
from app.models.run import RunState, RunStatus, RunStep
from app.workflows.crew_pipeline import run_crew_pipeline


router = APIRouter(prefix="/api", tags=["shiftforge"])


async def emit(run_id, stage, status, message, data=None):
    await event_bus.publish(run_id, {
        "stage": stage,
        "status": status,
        "message": message,
        "data": data or {},
    })


@router.get("/health")
def health():
    return {
        "status": "ok",
        "service": "shiftforge",
        "environment_version": environment_registry.active_version,
        "pipeline": "crewai",
    }


@router.get("/environment")
def get_environment():
    active = environment_registry.active_contract
    return {
        "active_version": environment_registry.active_version,
        "contract": active.model_dump(),
        "all_versions": {
            k: v.model_dump() for k, v in environment_registry.all_versions().items()
        },
        "history": environment_registry.history(),
    }


@router.post("/environment/change")
def change_environment():
    current = environment_registry.active_version
    target = "v2" if current == "v1" else "v1"
    contract = environment_registry.activate(target)
    repository.log_environment_version(target, contract.model_dump())
    return {
        "status": "changed",
        "previous_version": current,
        "active_version": target,
        "contract": contract.model_dump(),
    }


@router.get("/environment/versions")
def environment_versions():
    return {"versions": repository.list_environment_versions()}


@router.post("/run")
async def run_agent():
    run_id = "SF-" + uuid.uuid4().hex[:6].upper()
    started = time.perf_counter()

    active = environment_registry.active_contract
    original_strategy = StrategySpec(
        version="weather_v1",
        endpoint="/api/weather",
        method="GET",
        temperature_field="temperature",
        condition_field="condition",
        reasoning="Original hardcoded strategy.",
    )

    run = RunState(
        run_id=run_id,
        task="Get current weather for the user.",
        environment_version=active.version,
        initial_strategy_version=original_strategy.version,
        status=RunStatus.RUNNING,
    )

    await emit(run_id, "monitor", "running",
               "Agent started (env=" + active.version + ")")

    try:
        result = execute_strategy(original_strategy)

        elapsed = int((time.perf_counter() - started) * 1000)
        run.steps.append(RunStep(
            stage="monitor", status="success",
            message="Tool responded: " + str(result.raw),
            duration_ms=elapsed, data={"raw": result.raw}))
        await emit(run_id, "monitor", "success",
                   "Tool responded: " + str(result.raw),
                   data={"raw": result.raw})

        run.status = RunStatus.SUCCESS
        run.result = {"temperature": result.temperature,
                      "condition": result.condition}
        run.total_adaptation_ms = elapsed

        run.steps.append(RunStep(
            stage="complete", status="success",
            message="Original task completed.",
            duration_ms=elapsed))
        await emit(run_id, "complete", "success",
                   "Original task completed.",
                   data={"final": True, "result": run.result})

        repository.save_run(run)
        return run.model_dump()

    except StrategyExecutionError as e:
        elapsed = int((time.perf_counter() - started) * 1000)
        run.steps.append(RunStep(
            stage="monitor", status="failed",
            message="Contract mismatch detected: " + e.message,
            duration_ms=elapsed, data={"tool_payload": e.tool_payload}))
        await emit(run_id, "monitor", "failed",
                   "Contract mismatch detected: " + e.message,
                   data={"tool_payload": e.tool_payload})

        run.failure_reason = e.message
        repository.save_run(run)

        # Hand off to the CrewAI adaptation pipeline
        run = await run_crew_pipeline(
            run=run,
            original_strategy=original_strategy,
            failure_reason=e.message,
            actual_response=e.tool_payload,
        )
        return run.model_dump()


@router.get("/runs")
def list_runs(limit: int = 50):
    return {"runs": repository.list_runs(limit=limit)}


@router.get("/runs/{run_id}")
def get_run_detail(run_id: str):
    row = repository.get_run(run_id)
    if not row:
        raise HTTPException(status_code=404, detail="Run " + run_id + " not found.")
    return row


@router.get("/adaptations")
def list_adaptations(limit: int = 50):
    return {"adaptations": repository.list_adaptations(limit=limit)}


@router.get("/strategies")
def list_strategies():
    return {"strategies": repository.list_strategies()}


@router.get("/stream/{run_id}")
async def stream_run(run_id: str):
    queue = event_bus.subscribe(run_id)

    async def event_generator():
        try:
            while True:
                event = await queue.get()
                yield "data: " + json.dumps(event) + "\n\n"
                if event.get("data", {}).get("final"):
                    break
        finally:
            event_bus.unsubscribe(run_id, queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
