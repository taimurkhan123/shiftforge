from app.agents.llm import call_llm_json
from app.models.adaptation import DiagnosisResult, StrategySpec

SYSTEM = """You are the Strategy Agent in ShiftForge.
Given a diagnosis of an environment change, produce a NEW strategy.

Return ONLY a JSON object with these keys:
- version: short string like "weather_v2"
- endpoint: the NEW endpoint path
- method: usually "GET"
- temperature_field: NEW field name for temperature
- condition_field: NEW field name for the condition
- reasoning: one short sentence
"""


def run_strategy(new_contract, diagnosis, previous_strategy_version="weather_v1"):
    user = "New contract:\n" + str(new_contract)
    user += "\n\nDiagnosis:\n" + diagnosis.model_dump_json(indent=2)
    user += "\n\nPrevious strategy version: " + previous_strategy_version
    return call_llm_json(SYSTEM, user, StrategySpec)
