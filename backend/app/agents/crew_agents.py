"""
CrewAI agent definitions.

Each agent here is a real CrewAI Agent with role/goal/backstory.
They reuse our existing Pydantic output models.
Groq via LiteLLM is the LLM provider.
"""

from crewai import Agent, LLM
from app.config import settings


def _make_llm() -> LLM:
    return LLM(
        model="groq/openai/gpt-oss-120b",
        api_key=settings.groq_api_key,
        temperature=0.2,
    )


# ---------------- Agent definitions ----------------

monitor_agent = Agent(
    role="Monitor Agent",
    goal="Detect whether an external tool response no longer matches the expected contract.",
    backstory=(
        "You are the first line of defense in ShiftForge. You watch every tool "
        "response the agent receives. You compare it against the known contract "
        "and decide, with precision, whether the environment changed. You never "
        "guess. You report status, severity, and reason."
    ),
    llm=_make_llm(),
    verbose=False,
    allow_delegation=False,
)


diagnosis_agent = Agent(
    role="Diagnosis Agent",
    goal="Compare an old API contract to a new one and identify exactly what changed.",
    backstory=(
        "You are a forensic analyst for API contracts. Given two contracts, you "
        "identify removed fields, added fields, and endpoint changes. You work "
        "literally — you never assume two differently-named fields mean the same "
        "thing."
    ),
    llm=_make_llm(),
    verbose=False,
    allow_delegation=False,
)


strategy_agent = Agent(
    role="Strategy Builder",
    goal="Produce a new strategy that reaches the original task's goal through the changed environment.",
    backstory=(
        "You are a systems engineer who rewrites agent strategies when their "
        "world changes. Given a diagnosis and a new contract, you produce a "
        "structured plan the runtime can execute safely. You only use fields "
        "that exist in the new contract."
    ),
    llm=_make_llm(),
    verbose=False,
    allow_delegation=False,
)


validation_agent = Agent(
    role="Validation Agent",
    goal="Decide whether a strategy that passed the sandbox is safe to adopt in production.",
    backstory=(
        "You are the safety gate. You look at the sandbox result and the original "
        "task, and you decide whether the strategy is correct and safe. You are "
        "conservative: if the sandbox failed or the output is ambiguous, you "
        "reject. You return validated, confidence, and reason."
    ),
    llm=_make_llm(),
    verbose=False,
    allow_delegation=False,
)


# Sandbox and Recovery are deterministic — no LLM needed.
# We keep them as pure functions in their existing modules.
# Only the 4 reasoning agents above are CrewAI Agents.

ALL_AGENTS = [
    monitor_agent,
    diagnosis_agent,
    strategy_agent,
    validation_agent,
]
