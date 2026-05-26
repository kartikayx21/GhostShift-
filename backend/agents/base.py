import asyncio
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from models import AgentLog


class BaseAgent(ABC):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self._logs: list[AgentLog] = []
        self._log_callback = None

    def set_log_callback(self, callback):
        self._log_callback = callback

    async def log(self, message: str):
        entry = AgentLog(
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_name=self.name,
            message=message,
        )
        self._logs.append(entry)
        if self._log_callback:
            await self._log_callback(entry)

    @abstractmethod
    async def run(self, brand: str, product: str, context: dict = None) -> dict:
        pass

    def get_logs(self) -> list[AgentLog]:
        return self._logs

    def clear_logs(self):
        self._logs = []
