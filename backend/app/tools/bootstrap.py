"""
Tool bootstrap.

Importing this module registers every available tool with the global
tool_registry. Called once at application startup.
"""

from app.tools.registry import tool_registry
from app.tools.weather import weather_tool
from app.tools.github import github_tool
from app.tools.database import database_tool
from app.tools.custom import custom_tool


def _register_all():
    for tool in (weather_tool, github_tool, database_tool, custom_tool):
        if not tool_registry.has(tool.name):
            tool_registry.register(tool)


_register_all()
