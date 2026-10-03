from typing import Dict, List, Optional
from app.models.contract import ToolContract


class EnvironmentRegistry:
    """
    Holds versioned contracts for the simulated external environment.
    The 'active' version is what the live agent sees.
    """

    def __init__(self):
        self._versions: Dict[str, ToolContract] = {}
        self._active: str = "v1"
        self._history: List[str] = ["v1"]

    def register(self, contract: ToolContract) -> None:
        self._versions[contract.version] = contract

    def get(self, version: str) -> Optional[ToolContract]:
        return self._versions.get(version)

    @property
    def active_version(self) -> str:
        return self._active

    @property
    def active_contract(self) -> ToolContract:
        return self._versions[self._active]

    def all_versions(self) -> Dict[str, ToolContract]:
        return dict(self._versions)

    def history(self) -> List[str]:
        return list(self._history)

    def activate(self, version: str) -> ToolContract:
        if version not in self._versions:
            raise ValueError(f"Unknown environment version: {version}")
        self._active = version
        self._history.append(version)
        return self._versions[version]


# ---------- Seed the two environments ----------

environment_registry = EnvironmentRegistry()

# v1 — original, what the agent was built for
environment_registry.register(
    ToolContract(
        version="v1",
        endpoint="/api/weather",
        method="GET",
        temperature_field="temperature",
        condition_field="condition",
    )
)

# v2 — the "changed" environment (schema + endpoint renamed)
environment_registry.register(
    ToolContract(
        version="v2",
        endpoint="/api/forecast",
        method="GET",
        temperature_field="temp_c",
        condition_field="weather",
    )
)