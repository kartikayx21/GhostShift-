import uuid
from datetime import datetime, timezone
from models import Investigation, AgentStatus, AgentStatusEnum


class DatabaseService:
    """In-memory database service for investigations."""

    def __init__(self):
        self._investigations: dict[str, Investigation] = {}

    def create_investigation(self, brand: str, product: str) -> Investigation:
        investigation_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        agents = {
            "hunter": AgentStatus(name="The Hunter", status=AgentStatusEnum.PENDING),
            "component_tracer": AgentStatus(name="The Component Tracer", status=AgentStatusEnum.PENDING),
            "factory_spy": AgentStatus(name="The Factory Spy", status=AgentStatusEnum.PENDING),
            "forensics": AgentStatus(name="The Forensics Agent", status=AgentStatusEnum.PENDING),
            "judge": AgentStatus(name="The Judge", status=AgentStatusEnum.PENDING),
        }

        investigation = Investigation(
            id=investigation_id,
            brand=brand,
            product=product,
            status="running",
            agents=agents,
            result=None,
            created_at=now,
        )

        self._investigations[investigation_id] = investigation
        return investigation

    def get_investigation(self, investigation_id: str) -> Investigation | None:
        return self._investigations.get(investigation_id)

    def update_investigation(self, investigation_id: str, investigation: Investigation):
        self._investigations[investigation_id] = investigation

    def list_investigations(self) -> list[Investigation]:
        return sorted(
            self._investigations.values(),
            key=lambda inv: inv.created_at,
            reverse=True,
        )


# Singleton instance
db = DatabaseService()
