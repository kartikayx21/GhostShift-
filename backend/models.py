from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class InvestigationRequest(BaseModel):
    brand: str
    product: str


class AgentStatusEnum(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETE = "complete"
    ERROR = "error"


class AgentLog(BaseModel):
    timestamp: str
    agent_name: str
    message: str


class AgentStatus(BaseModel):
    name: str
    status: AgentStatusEnum = AgentStatusEnum.PENDING
    findings_count: int = 0
    findings: list[dict] = Field(default_factory=list)
    logs: list[AgentLog] = Field(default_factory=list)


class Evidence(BaseModel):
    type: str  # 'listing' | 'supplier' | 'employment' | 'forensic' | 'synthesis'
    description: str
    source_url: str = ""
    confidence: float = Field(ge=0, le=1)


class InvestigationResult(BaseModel):
    risk_score: float
    verdict: str
    evidence: list[Evidence]
    recommended_action: str  # 'Report' | 'Investigate Further' | 'Low Risk'


class Investigation(BaseModel):
    id: str
    brand: str
    product: str
    status: str = "running"
    agents: dict[str, AgentStatus] = Field(default_factory=dict)
    result: Optional[InvestigationResult] = None
    created_at: str
