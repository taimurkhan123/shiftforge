"""
Weather tool — registered as the first entry in the Tool Registry.

IMPORTANT: This is a WRAPPER. It does not reimplement weather logic.
It reuses the existing simulator functions and contracts from
app.sandbox.tools and app.sandbox.environment, so the weather demo
behaves identically to before.
"""

from app.tools.base import ToolDefinition, ToolScenario
from app.sandbox.tools import TOOL_REGISTRY as WEATHER_SIMULATORS


# Reuse the existing weather simulators by name.
# If these change in the future, the tool registry stays in sync.
def _simulate_v1():
    return WEATHER_SIMULATORS["fetch_weather_v1"]()


def _simulate_v2():
    return WEATHER_SIMULATORS["fetch_weather_v2"]()


# Register the two scenarios that already exist in the live environment.
# Contracts mirror what app.sandbox.environment currently registers.
weather_tool = ToolDefinition(
    name="weather",
    display_name="Weather API",
    description="Retrieves current weather. Endpoint and field names may change between versions.",
    default_version="v1",
    scenarios={
        "v1": ToolScenario(
            version="v1",
            endpoint="/api/weather",
            method="GET",
            contract={
                "version": "v1",
                "endpoint": "/api/weather",
                "method": "GET",
                "temperature_field": "temperature",
                "condition_field": "condition",
            },
            simulate=_simulate_v1,
            description="Original weather contract.",
        ),
        "v2": ToolScenario(
            version="v2",
            endpoint="/api/forecast",
            method="GET",
            contract={
                "version": "v2",
                "endpoint": "/api/forecast",
                "method": "GET",
                "temperature_field": "temp_c",
                "condition_field": "weather",
            },
            simulate=_simulate_v2,
            description="Changed weather contract: endpoint and field names renamed.",
        ),
    },
)
