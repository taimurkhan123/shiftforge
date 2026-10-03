import json
from typing import List, Optional
from sqlmodel import select

from app.database import get_session
from app.database.tables import (
    RunTable,
    AdaptationTable,
    EnvironmentVersionTable,
    StrategyTable,
)
from app.models.run import RunState


# ---------- Runs ----------

def save_run(run: RunState) -> None:
    with get_session() as session:
        existing = session.exec(
            select(RunTable).where(RunTable.run_id == run.run_id)
        ).first()

        if existing:
            row = existing
        else:
            row = RunTable(
                run_id=run.run_id,
                task=run.task,
                status=run.status.value,
                environment_version=run.environment_version,
                initial_strategy_version=run.initial_strategy_version,
            )

        row.status = run.status.value
        row.environment_version = run.environment_version
        row.final_strategy_version = run.final_strategy_version
        row.failure_reason = run.failure_reason
        row.result_json = json.dumps(run.result) if run.result else None
        row.steps_json = json.dumps([s.model_dump(mode="json") for s in run.steps])
        row.total_adaptation_ms = run.total_adaptation_ms
        row.updated_at = run.updated_at

        session.add(row)
        session.commit()


def get_run(run_id: str) -> Optional[dict]:
    with get_session() as session:
        row = session.exec(
            select(RunTable).where(RunTable.run_id == run_id)
        ).first()
        if not row:
            return None
        return _row_to_dict(row)


def list_runs(limit: int = 50) -> List[dict]:
    with get_session() as session:
        rows = session.exec(
            select(RunTable).order_by(RunTable.created_at.desc()).limit(limit)
        ).all()
        return [_row_to_dict(r) for r in rows]


def _row_to_dict(r: RunTable) -> dict:
    return {
        "run_id": r.run_id,
        "task": r.task,
        "status": r.status,
        "environment_version": r.environment_version,
        "initial_strategy_version": r.initial_strategy_version,
        "final_strategy_version": r.final_strategy_version,
        "failure_reason": r.failure_reason,
        "result": json.loads(r.result_json) if r.result_json else None,
        "steps": json.loads(r.steps_json) if r.steps_json else [],
        "total_adaptation_ms": r.total_adaptation_ms,
        "created_at": r.created_at.isoformat(),
        "updated_at": r.updated_at.isoformat(),
    }


# ---------- Environment versions ----------

def log_environment_version(version: str, contract_dict: dict) -> None:
    with get_session() as session:
        row = EnvironmentVersionTable(
            version=version,
            contract_json=json.dumps(contract_dict),
        )
        session.add(row)
        session.commit()


def list_environment_versions() -> List[dict]:
    with get_session() as session:
        rows = session.exec(
            select(EnvironmentVersionTable).order_by(
                EnvironmentVersionTable.activated_at.desc()
            )
        ).all()
        return [
            {
                "version": r.version,
                "contract": json.loads(r.contract_json),
                "activated_at": r.activated_at.isoformat(),
            }
            for r in rows
        ]


# ---------- Adaptations ----------

def save_adaptation(
    adaptation_id: str,
    run_id: str,
    change_type: str,
    from_strategy: str,
    to_strategy: str,
    result: str,
    detail: Optional[dict] = None,
) -> None:
    with get_session() as session:
        row = AdaptationTable(
            adaptation_id=adaptation_id,
            run_id=run_id,
            change_type=change_type,
            from_strategy=from_strategy,
            to_strategy=to_strategy,
            result=result,
            detail_json=json.dumps(detail) if detail else None,
        )
        session.add(row)
        session.commit()


def list_adaptations(limit: int = 50) -> List[dict]:
    with get_session() as session:
        rows = session.exec(
            select(AdaptationTable).order_by(
                AdaptationTable.created_at.desc()
            ).limit(limit)
        ).all()
        return [
            {
                "adaptation_id": r.adaptation_id,
                "run_id": r.run_id,
                "change_type": r.change_type,
                "from_strategy": r.from_strategy,
                "to_strategy": r.to_strategy,
                "result": r.result,
                "detail": json.loads(r.detail_json) if r.detail_json else None,
                "created_at": r.created_at.isoformat(),
            }
            for r in rows
        ]


# ---------- Strategies ----------

def save_strategy(
    version: str,
    endpoint: str,
    method: str,
    temperature_field: str,
    condition_field: str,
    reasoning: Optional[str] = None,
) -> None:
    with get_session() as session:
        existing = session.exec(
            select(StrategyTable).where(StrategyTable.version == version)
        ).first()
        if existing:
            existing.endpoint = endpoint
            existing.method = method
            existing.temperature_field = temperature_field
            existing.condition_field = condition_field
            existing.reasoning = reasoning
            session.add(existing)
        else:
            session.add(StrategyTable(
                version=version,
                endpoint=endpoint,
                method=method,
                temperature_field=temperature_field,
                condition_field=condition_field,
                reasoning=reasoning,
            ))
        session.commit()


def list_strategies() -> List[dict]:
    with get_session() as session:
        rows = session.exec(select(StrategyTable).order_by(StrategyTable.id)).all()
        return [
            {
                "version": r.version,
                "endpoint": r.endpoint,
                "method": r.method,
                "temperature_field": r.temperature_field,
                "condition_field": r.condition_field,
                "reasoning": r.reasoning,
                "active": r.active,
                "created_at": r.created_at.isoformat(),
            }
            for r in rows
        ]