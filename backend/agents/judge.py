import asyncio
from agents.base import BaseAgent
from services.anthropic_client import llm


class JudgeAgent(BaseAgent):
    """Agent 5 — The Judge: Synthesizes all intelligence into a final verdict."""

    def __init__(self):
        super().__init__(
            name="The Judge",
            description="Synthesizes all investigation findings into a final risk verdict",
        )

    async def run(self, brand: str, product: str, context: dict = None) -> dict:
        if context is None:
            context = {}

        await self.log("Synthesizing all intelligence findings...")
        await asyncio.sleep(0.3)

        # Count total data points across all agents
        total_data_points = 0
        for agent_key, findings in context.items():
            if isinstance(findings, dict):
                for value in findings.values():
                    if isinstance(value, list):
                        total_data_points += len(value)
                    elif isinstance(value, (int, float)):
                        total_data_points += 1

        await self.log(f"Analyzing {total_data_points} data points from 4 field agents...")
        await asyncio.sleep(0.5)

        verdict = await llm.synthesize_verdict(brand, product, context)

        risk_score = verdict.get("risk_score", 0)
        recommended_action = verdict.get("recommended_action", "Investigate Further")
        verdict_text = verdict.get("verdict", "")

        await self.log(f"VERDICT: Ghost shift probability: {risk_score}%")
        await self.log(f"Recommended action: {recommended_action}")

        evidence_list = verdict.get("evidence", [])
        for ev in evidence_list:
            ev_type = ev.get("type", "unknown")
            ev_desc = ev.get("description", "")
            await self.log(f"EVIDENCE [{ev_type}]: {ev_desc}")

        return verdict
