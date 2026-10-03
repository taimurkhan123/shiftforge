"""
SQLModel tables for ShiftForge.

We keep this lean for the hackathon:
- runs: one row per /api/run invocation
- adaptations: one row per successful adaptation (Phase 3+)
- environment_versions: log of env changes
- strategies: strategies the agent has adopted
"""

from datetime import datetime, timezone, timezone
from typing import Optional
from sqlmodel import SQLModel, Field


class RunTable(SQLModel, table=True):
    __tablename__ = "runs"

    id: Optional[int] = Field(default=None, primary_key=True)
    run_id: str = Field(index=True, unique=True)
    task: str
    status: str
    environment_version: str
    initial_strategy_version: str
    final_strategy_version: Optional[str] = None
    failure_reason: Optional[str] = None
    result_json: Optional[str] = None  # JSON-encoded
    steps_json: Optional[str] = None   # JSON-encoded list
    total_adaptation_ms: Optional[int] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AdaptationTable(SQLModel, table=True):
    __tablename__ = "adaptations"

    id: Optional[int] = Field(default=None, primary_key=True)
    adaptation_id: str = Field(index=True, unique=True)
    run_id: str = Field(index=True)
    change_type: str          # e.g. "endpoint+field_rename"
    from_strategy: str
    to_strategy: str
    result: str               # "success" | "failed"
    detail_json: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EnvironmentVersionTable(SQLModel, table=True):
    __tablename__ = "environment_versions"

    id: Optional[int] = Field(default=None, primary_key=True)
    version: str = Field(index=True)
    contract_json: str
    activated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StrategyTable(SQLModel, table=True):
    __tablename__ = "strategies"

    id: Optional[int] = Field(default=None, primary_key=True)
    version: str = Field(index=True, unique=True)
    endpoint: str
    method: str
    temperature_field: str
    condition_field: str
    reasoning: Optional[str] = None
    active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))