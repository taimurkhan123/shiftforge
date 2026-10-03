# ShiftForge — Self-Adapting AI Agent Platform

> **When the environment changes, your AI agent adapts.**

ShiftForge is an agentic AI platform that demonstrates how an AI agent can continue working when the tools, APIs, schemas, or environment it depends on suddenly change.

## The One Demo That Matters

Working Agent → Environment Change → Failure → Detection → Diagnosis → New Strategy → Sandbox Test → Validation → Recovery → Task Completed

**The scenario:** An agent fetches the weather via `/api/weather` and reads `temperature`. Then the environment changes — the endpoint becomes `/api/forecast` and the field becomes `temp_c`. The original strategy breaks. ShiftForge detects the failure, diagnoses the change, generates a new strategy, tests it safely, validates it, adopts it, and completes the original task — autonomously, in seconds.

## Architecture

```mermaid
flowchart TD
    User[User / Task] --> Executor[Strategy Executor]
    Executor -->|Contract OK| Tool[Registered Tool]
    Executor -->|Contract Mismatch| Monitor[Monitor Agent]
    Tool --> Result[Result]
    Monitor --> Diagnosis[Diagnosis Agent]
    Diagnosis --> Strategy[Strategy Agent]
    Strategy --> Sandbox[Sandbox deterministic]
    Sandbox -->|passed| Validation[Validation Agent]
    Sandbox -->|failed| Reject[Reject]
    Validation -->|validated| Recovery[Recovery deterministic]
    Validation -->|rejected| Reject
    Recovery --> Result
    Monitor -.LLM.-> Groq[Groq gpt-oss-120b]
    Diagnosis -.LLM.-> Groq
    Strategy -.LLM.-> Groq
    Validation -.LLM.-> Groq