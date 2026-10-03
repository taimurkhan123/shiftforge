from app.agents.llm import call_llm_json
from app.models.adaptation import DiagnosisResult

SYSTEM = """You are the Diagnosis Agent in ShiftForge.
Compare an OLD contract to a NEW contract and explain precisely what changed.

Return ONLY a JSON object with these keys:
- removed_fields: list of strings
- added_fields: list of strings
- endpoint_changed_from: string or null
- endpoint_changed_to: string or null
- summary: one-sentence summary
"""


def run_diagnosis(old_contract, new_contract):
    user = "Old contract:\n" + str(old_contract)
    user += "\n\nNew contract:\n" + str(new_contract)
    return call_llm_json(SYSTEM, user, DiagnosisResult)
