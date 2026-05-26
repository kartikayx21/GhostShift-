import asyncio
from agents.base import BaseAgent
from services.brightdata import brightdata


class FactorySpyAgent(BaseAgent):
    """Agent 3 — The Factory Spy: Monitors job postings and employee movements in manufacturing regions."""

    def __init__(self):
        super().__init__(
            name="The Factory Spy",
            description="Monitors job postings and employee movements in manufacturing hubs",
        )

    async def run(self, brand: str, product: str, context: dict = None) -> dict:
        await self.log("Scanning job boards in manufacturing regions...")
        await asyncio.sleep(0.3)

        results = await brightdata.search_job_postings(brand, product)

        job_postings = results.get("job_postings", []) if isinstance(results, dict) else results
        employee_movements = results.get("employee_movements", []) if isinstance(results, dict) else []

        suspicious_count = 0

        for posting in job_postings:
            title = posting.get("title", "Unknown")
            company = posting.get("company", "Unknown")
            location = posting.get("location", "Unknown")
            keywords = posting.get("suspicious_keywords", [])

            if keywords:
                suspicious_count += 1
                await self.log(
                    f"SUSPICIOUS JOB: '{title}' at {company} ({location}) — "
                    f"keywords: {', '.join(keywords)}"
                )
                await asyncio.sleep(0.3)

        await self.log(f"Analyzing employee movement signals...")
        await asyncio.sleep(0.5)

        for movement in employee_movements:
            name = movement.get("name", "Unknown")
            prev = movement.get("previous_employer", "Unknown")
            curr = movement.get("current_employer", "Unknown")
            role = movement.get("role", "Unknown")
            suspicious_count += 1
            await self.log(
                f"EMPLOYEE MOVEMENT: {name} moved from {prev} to {curr} as {role}"
            )
            await asyncio.sleep(0.2)

        await self.log(
            f"Factory intelligence scan complete. {suspicious_count} suspicious signals detected"
        )

        return {
            "job_postings": job_postings,
            "employee_movements": employee_movements,
            "suspicious_signals": suspicious_count,
        }
