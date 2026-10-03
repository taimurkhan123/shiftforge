import asyncio
from typing import Dict, List, Any
from datetime import datetime


class EventBus:
    """
    In-memory pub/sub for run events.
    Frontend subscribes via SSE at /api/stream/{run_id}.
    """

    def __init__(self):
        # run_id -> list of asyncio.Queue subscribers
        self._subscribers: Dict[str, List[asyncio.Queue]] = {}
        # run_id -> full event log (so late subscribers can replay)
        self._logs: Dict[str, List[dict]] = {}

    async def publish(self, run_id: str, event: dict) -> None:
        event = {"timestamp": datetime.utcnow().isoformat(), **event}
        self._logs.setdefault(run_id, []).append(event)
        for q in self._subscribers.get(run_id, []):
            await q.put(event)

    def subscribe(self, run_id: str) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        self._subscribers.setdefault(run_id, []).append(q)
        # Replay history so late subscribers aren't blind
        for prior in self._logs.get(run_id, []):
            q.put_nowait(prior)
        return q

    def unsubscribe(self, run_id: str, q: asyncio.Queue) -> None:
        if run_id in self._subscribers and q in self._subscribers[run_id]:
            self._subscribers[run_id].remove(q)

    def get_logs(self, run_id: str) -> List[dict]:
        return list(self._logs.get(run_id, []))


event_bus = EventBus()