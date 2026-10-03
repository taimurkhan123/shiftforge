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
from app.tools.registry import tool_registry
from app.tools import bootstrap  # noqa: F401 — ensures tools are registered
from app.workflows.tool_pipeline import run_tool_pipeline


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

# ---------- Tool Registry endpoints (multi-tool upgrade) ----------

@router.get("/tools")
def list_tools():
    """List every tool the agent can adapt to, with all their scenarios."""
    return {"tools": tool_registry.to_list()}


@router.get("/tools/{tool_name}")
def get_tool(tool_name: str):
    """Get a single tool definition by name."""
    if not tool_registry.has(tool_name):
        raise HTTPException(
            status_code=404,
            detail=f"Tool '{tool_name}' not found. Available: {tool_registry.all_names()}",
        )
    return tool_registry.get(tool_name).to_dict()

# ---------- Tool actions (multi-tool upgrade) ----------

@router.post("/tools/{tool_name}/change")
def change_tool_environment(tool_name: str):
    """
    Toggle a tool's active environment version (v1 <-> v2).
    Does NOT touch the global weather environment used by /api/run.
    """
    if not tool_registry.has(tool_name):
        raise HTTPException(
            status_code=404,
            detail=f"Tool '{tool_name}' not found. Available: {tool_registry.all_names()}",
        )
    tool = tool_registry.get(tool_name)
    current = tool.active_version
    target = "v2" if current == "v1" else "v1"
    scenario = tool.activate(target)
    return {
        "status": "changed",
        "tool": tool_name,
        "previous_version": current,
        "active_version": target,
        "contract": scenario.contract,
    }


@router.post("/tools/{tool_name}/simulate")
def simulate_tool(tool_name: str):
    """
    Run the tool's active simulator and return the raw response.
    Safe: only predefined simulators can be invoked.
    """
    if not tool_registry.has(tool_name):
        raise HTTPException(
            status_code=404,
            detail=f"Tool '{tool_name}' not found. Available: {tool_registry.all_names()}",
        )
    tool = tool_registry.get(tool_name)
    try:
        raw = tool.active_scenario.simulate()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulator failed: {e}")
    return {
        "tool": tool_name,
        "version": tool.active_version,
        "response": raw,
    }

# ---------- Tool run endpoint (multi-tool upgrade) ----------

from pydantic import BaseModel as _PydanticBaseModel
from typing import Optional as _Optional


class _ToolRunRequest(_PydanticBaseModel):
    task: str = "Complete the requested task using this tool."
    expected_version: str = "v1"


@router.post("/tools/{tool_name}/run")
async def run_tool_agent(tool_name: str, body: _ToolRunRequest):
    """
    Run the adaptation pipeline for a specific tool.

    If the tool is on its expected version (default v1), returns success immediately.
    If the environment changed, runs the generic CrewAI adaptation pipeline.
    """
    if not tool_registry.has(tool_name):
        raise HTTPException(
            status_code=404,
            detail=f"Tool '{tool_name}' not found. Available: {tool_registry.all_names()}",
        )

    tool = tool_registry.get(tool_name)
    active_version = tool.active_version
    expected_version = body.expected_version

    run_id = "SF-" + uuid.uuid4().hex[:6].upper()
    started = time.perf_counter()

    run = RunState(
        run_id=run_id,
        task=body.task,
        environment_version=active_version,
        initial_strategy_version=f"{tool_name}_v1",
        status=RunStatus.RUNNING,
    )

    await emit(run_id, "monitor", "running",
               f"Agent started (tool={tool_name}, env={active_version})")

    # Case 1: environment matches expected -> immediate success
    if active_version == expected_version:
        raw = tool.active_scenario.simulate()
        elapsed = int((time.perf_counter() - started) * 1000)
        run.steps.append(RunStep(
            stage="monitor", status="success",
            message=f"Tool responded: {raw}",
            duration_ms=elapsed, data={"raw": raw},
        ))
        await emit(run_id, "monitor", "success",
                   f"Tool responded: {raw}", data={"raw": raw})

        run.status = RunStatus.SUCCESS
        run.result = raw
        run.total_adaptation_ms = elapsed
        run.steps.append(RunStep(
            stage="complete", status="success",
            message="Task completed successfully.",
            duration_ms=elapsed,
        ))
        await emit(run_id, "complete", "success",
                   "Task completed successfully.",
                   data={"final": True, "result": run.result})
        repository.save_run(run)
        return run.model_dump()

    # Case 2: environment changed -> run adaptation
    elapsed = int((time.perf_counter() - started) * 1000)
    failure_reason = f"Tool '{tool_name}' is on version '{active_version}' but expected '{expected_version}'."
    run.steps.append(RunStep(
        stage="monitor", status="failed",
        message=failure_reason,
        duration_ms=elapsed, data={"active": active_version, "expected": expected_version},
    ))
    await emit(run_id, "monitor", "failed", failure_reason,
               data={"active": active_version, "expected": expected_version})

    run.failure_reason = failure_reason
    repository.save_run(run)

    run = await run_tool_pipeline(
        run=run,
        tool_name=tool_name,
        task=body.task,
        failure_reason=failure_reason,
        actual_response=None,
    )
    return run.model_dump()

