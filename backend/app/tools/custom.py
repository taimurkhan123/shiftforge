"""
Custom tool — predefined controlled scenarios for ShiftForge.

No arbitrary user code. Only predefined variants are selectable.
The point is to show the adaptation engine can handle parameter
renames and format changes, without needing a new tool definition.

Two scenarios:
- v1: { "customer_id": ..., "profile": ..., "region": ... }
- v2: { "customerId": ..., "profile_type": ..., "region_code": ... }
"""

from typing import Dict, Any
from app.tools.base import ToolDefinition, ToolScenario


_CUSTOM_TRUTH = {
    "customer_id": "C-001",
    "profile": "standard",
    "region": "PK",
}


def _simulate_v1() -> Dict[str, Any]:
    """Original custom tool contract."""
    return {
        "customer_id": _CUSTOM_TRUTH["customer_id"],
        "profile": _CUSTOM_TRUTH["profile"],
        "region": _CUSTOM_TRUTH["region"],
    }


def _simulate_v2() -> Dict[str, Any]:
    """Changed custom tool contract: parameters renamed, region format changed."""
    return {
        "customerId": _CUSTOM_TRUTH["customer_id"],
        "profile_type": _CUSTOM_TRUTH["profile"],
        "region_code": "PAK",
    }


custom_tool = ToolDefinition(
    name="custom",
    display_name="Custom Tool",
    description="Simulated custom API. Predefined changes for demonstration.",
    default_version="v1",
    scenarios={
        "v1": ToolScenario(
            version="v1",
            endpoint="/api/customer",
            method="GET",
            contract={
                "version": "v1",
                "endpoint": "/api/customer",
                "method": "GET",
                "customer_id_field": "customer_id",
                "profile_field": "profile",
                "region_field": "region",
            },
            simulate=_simulate_v1,
            description="Original custom contract.",
        ),
        "v2": ToolScenario(
            version="v2",
            endpoint="/api/customer",
            method="GET",
            contract={
                "version": "v2",
                "endpoint": "/api/customer",
                "method": "GET",
                "customer_id_field": "customerId",
                "profile_field": "profile_type",
                "region_field": "region_code",
            },
            simulate=_simulate_v2,
            description="Changed custom contract: parameters renamed.",
        ),
    },
)
