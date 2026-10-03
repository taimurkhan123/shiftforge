"""
GitHub tool — simulated GitHub API for the ShiftForge demo.

Real GitHub API is NOT called. This is a controlled simulation so that
the adaptation engine can be demonstrated without requiring tokens or
network access.

Two scenarios:
- v1: { "repository": ..., "open_issues": ... }
- v2: { "repo_name": ..., "issues_open": ... }

The point of the demo is that v2 renames both fields. The agent must
detect this and adapt.
"""

from typing import Dict, Any
from app.tools.base import ToolDefinition, ToolScenario


# Simulated GitHub truth. Same data across versions, different shape.
_GITHUB_TRUTH = {
    "repository": "shiftforge",
    "open_issues": 5,
}


def _simulate_v1() -> Dict[str, Any]:
    """Original GitHub contract shape."""
    return {
        "repository": _GITHUB_TRUTH["repository"],
        "open_issues": _GITHUB_TRUTH["open_issues"],
    }


def _simulate_v2() -> Dict[str, Any]:
    """Changed GitHub contract shape (field names renamed)."""
    return {
        "repo_name": _GITHUB_TRUTH["repository"],
        "issues_open": _GITHUB_TRUTH["open_issues"],
    }


github_tool = ToolDefinition(
    name="github",
    display_name="GitHub API",
    description="Retrieves repository information. Field names may change between API versions.",
    default_version="v1",
    scenarios={
        "v1": ToolScenario(
            version="v1",
            endpoint="/api/github/repo",
            method="GET",
            contract={
                "version": "v1",
                "endpoint": "/api/github/repo",
                "method": "GET",
                "repository_field": "repository",
                "issues_field": "open_issues",
            },
            simulate=_simulate_v1,
            description="Original GitHub contract.",
        ),
        "v2": ToolScenario(
            version="v2",
            endpoint="/api/github/repo",
            method="GET",
            contract={
                "version": "v2",
                "endpoint": "/api/github/repo",
                "method": "GET",
                "repository_field": "repo_name",
                "issues_field": "issues_open",
            },
            simulate=_simulate_v2,
            description="Changed GitHub contract: field names renamed.",
        ),
    },
)
