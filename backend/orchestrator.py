import asyncio
import traceback
from models import AgentLog, AgentStatusEnum, Evidence, InvestigationResult
from services.database import db
from agents.hunter import HunterAgent
from agents.component_tracer import ComponentTracerAgent
from agents.factory_spy import FactorySpyAgent
from agents.forensics import ForensicsAgent
from agents.judge import JudgeAgent


# Module-level dict of active orchestrators
active_orchestrators: dict[str, "InvestigationOrchestrator"] = {}


class InvestigationOrchestrator:
    """Orchestrates the sequential execution of all 5 investigation agents."""

    def __init__(self, investigation_id: str):
        self.investigation_id = investigation_id
        self.event_queue: asyncio.Queue = asyncio.Queue()

        # Create agent instances
        self.agents = {
            "hunter": HunterAgent(),
            "component_tracer": ComponentTracerAgent(),
            "factory_spy": FactorySpyAgent(),
            "forensics": ForensicsAgent(),
            "judge": JudgeAgent(),
        }

    async def _log_callback(self, log_entry: AgentLog):
        """Push log entries onto the SSE event queue."""
        await self.event_queue.put(
            {
                "event": "log",
                "data": {
                    "timestamp": log_entry.timestamp,
                    "agent_name": log_entry.agent_name,
                    "message": log_entry.message,
                },
            }
        )

    async def _run_agent(
        self,
        agent_key: str,
        agent,
        brand: str,
        product: str,
        context: dict = None,
    ) -> dict:
        """Run a single agent with status tracking and SSE events."""
        investigation = db.get_investigation(self.investigation_id)
        if not investigation:
            return {}

        try:
            # Set agent status to RUNNING
            investigation.agents[agent_key].status = AgentStatusEnum.RUNNING
            db.update_investigation(self.investigation_id, investigation)
            await self.event_queue.put(
                {
                    "event": "status",
                    "data": {
                        "agent": agent_key,
                        "name": investigation.agents[agent_key].name,
                        "status": "running",
                    },
                }
            )

            # Set log callback and run agent
            agent.set_log_callback(self._log_callback)
            findings = await agent.run(brand, product, context)

            # Update status to COMPLETE
            investigation = db.get_investigation(self.investigation_id)
            findings_count = 0
            if isinstance(findings, dict):
                for v in findings.values():
                    if isinstance(v, list):
                        findings_count += len(v)
                    elif isinstance(v, (int, float)):
                        findings_count += 1

            investigation.agents[agent_key].status = AgentStatusEnum.COMPLETE
            investigation.agents[agent_key].findings_count = findings_count
            investigation.agents[agent_key].findings = (
                [findings] if isinstance(findings, dict) else findings
            )
            investigation.agents[agent_key].logs = agent.get_logs()
            db.update_investigation(self.investigation_id, investigation)

            await self.event_queue.put(
                {
                    "event": "status",
                    "data": {
                        "agent": agent_key,
                        "name": investigation.agents[agent_key].name,
                        "status": "complete",
                        "findings_count": findings_count,
                    },
                }
            )

            return findings

        except Exception as e:
            # Set status to ERROR
            investigation = db.get_investigation(self.investigation_id)
            if investigation:
                investigation.agents[agent_key].status = AgentStatusEnum.ERROR
                investigation.agents[agent_key].logs = agent.get_logs()
                db.update_investigation(self.investigation_id, investigation)

            error_msg = f"Agent {agent_key} failed: {str(e)}"
            print(f"[ERROR] {error_msg}\n{traceback.format_exc()}")

            await self.event_queue.put(
                {
                    "event": "error",
                    "data": {
                        "agent": agent_key,
                        "name": self.agents[agent_key].name,
                        "status": "error",
                        "error": str(e),
                    },
                }
            )

            return {}

    async def run(self, brand: str, product: str):
        """Run the full investigation pipeline: agents 1-4 sequentially, then agent 5."""
        try:
            # Run agents 1-4 sequentially
            hunter_findings = await self._run_agent(
                "hunter", self.agents["hunter"], brand, product
            )

            component_findings = await self._run_agent(
                "component_tracer", self.agents["component_tracer"], brand, product
            )

            factory_findings = await self._run_agent(
                "factory_spy", self.agents["factory_spy"], brand, product
            )

            forensics_findings = await self._run_agent(
                "forensics", self.agents["forensics"], brand, product
            )

            # Collect all findings for The Judge
            all_findings = {
                "hunter": hunter_findings,
                "component_tracer": component_findings,
                "factory_spy": factory_findings,
                "forensics": forensics_findings,
            }

            # Run Agent 5 — The Judge
            verdict = await self._run_agent(
                "judge", self.agents["judge"], brand, product, context=all_findings
            )

            # Update investigation with final result
            investigation = db.get_investigation(self.investigation_id)
            if investigation and verdict:
                evidence_list = []
                for ev in verdict.get("evidence", []):
                    evidence_list.append(
                        Evidence(
                            type=ev.get("type", "synthesis"),
                            description=ev.get("description", ""),
                            source_url=ev.get("source_url", ""),
                            confidence=min(1.0, ev.get("confidence", 0.5) / 100.0 if ev.get("confidence", 0.5) > 1 else ev.get("confidence", 0.5)),
                        )
                    )

                investigation.result = InvestigationResult(
                    risk_score=verdict.get("risk_score", 0),
                    verdict=verdict.get("verdict", ""),
                    evidence=evidence_list,
                    recommended_action=verdict.get(
                        "recommended_action", "Investigate Further"
                    ),
                )
                investigation.status = "complete"
                db.update_investigation(self.investigation_id, investigation)

            # Signal completion
            await self.event_queue.put(
                {
                    "event": "complete",
                    "data": {
                        "status": "complete",
                        "risk_score": verdict.get("risk_score", 0) if verdict else 0,
                        "recommended_action": verdict.get(
                            "recommended_action", "Investigate Further"
                        )
                        if verdict
                        else "Investigate Further",
                    },
                }
            )

        except Exception as e:
            print(f"[ERROR] Orchestrator failed: {str(e)}\n{traceback.format_exc()}")
            investigation = db.get_investigation(self.investigation_id)
            if investigation:
                investigation.status = "error"
                db.update_investigation(self.investigation_id, investigation)

            await self.event_queue.put(
                {
                    "event": "error",
                    "data": {"status": "error", "error": str(e)},
                }
            )
