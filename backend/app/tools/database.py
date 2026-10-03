"""
Database tool — simulated database query for the ShiftForge demo.

No real database is queried. This is a controlled simulation so the
adaptation engine can be demonstrated safely.

Two scenarios:
- v1: { "user_id": ..., "name": ..., "status": ... }
- v2: { "user_id": ..., "full_name": ..., "account_status": ... }

The point: two field names renamed. The agent must detect and adapt.
"""

from typing import Dict, Any
from app.tools.base import ToolDefinition, ToolScenario


_DB_TRUTH = {
    "user_id": 101,
    "name": "Ali",
    "status": "active",
}


def _simulate_v1() -> Dict[str, Any]:
    """Original database schema shape."""
    return {
        "user_id": _DB_TRUTH["user_id"],
        "name": _DB_TRUTH["name"],
        "status": _DB_TRUTH["status"],
    }


def _simulate_v2() -> Dict[str, Any]:
    """Changed database schema shape (columns renamed)."""
    return {
        "user_id": _DB_TRUTH["user_id"],
        "full_name": _DB_TRUTH["name"],
        "account_status": _DB_TRUTH["status"],
    }


database_tool = ToolDefinition(
    name="database",
    display_name="Database Tool",
    description="Queries user records. Column names may change between schema versions.",
    default_version="v1",
    scenarios={
        "v1": ToolScenario(
            version="v1",
            endpoint="/db/users",
            method="SELECT",
            contract={
                "version": "v1",
                "endpoint": "/db/users",
                "method": "SELECT",
                "name_field": "name",
                "status_field": "status",
            },
            simulate=_simulate_v1,
            description="Original database schema.",
        ),
        "v2": ToolScenario(
            version="v2",
            endpoint="/db/users",
            method="SELECT",
            contract={
                "version": "v2",
                "endpoint": "/db/users",
                "method": "SELECT",
                "name_field": "full_name",
                "status_field": "account_status",
            },
            simulate=_simulate_v2,
            description="Changed database schema: columns renamed.",
        ),
    },
)
