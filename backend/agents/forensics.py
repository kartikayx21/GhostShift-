import asyncio
from agents.base import BaseAgent
from services.brightdata import brightdata
from services.anthropic_client import claude


class ForensicsAgent(BaseAgent):
    """Agent 4 — The Forensics Agent: Performs AI-powered visual analysis of product images."""

    def __init__(self):
        super().__init__(
            name="The Forensics Agent",
            description="Performs AI-powered forensic analysis of product images for counterfeit indicators",
        )

    async def run(self, brand: str, product: str, context: dict = None) -> dict:
        await self.log("Gathering product images for forensic analysis...")
        await asyncio.sleep(0.3)

        images = await brightdata.get_product_images(brand, product)

        await self.log(f"Analyzing {len(images)} product images with AI vision...")
        await asyncio.sleep(0.5)

        results = await claude.analyze_forensics(images, brand, product)

        total_flags = 0
        high_confidence_flags = 0

        for analysis in results:
            image_url = analysis.get("image_url", "")
            findings = analysis.get("findings", [])
            overall_risk = analysis.get("overall_risk", 0)

            for finding in findings:
                total_flags += 1
                finding_type = finding.get("type", "unknown")
                description = finding.get("description", "")
                confidence = finding.get("confidence", 0)

                if confidence >= 0.7:
                    high_confidence_flags += 1

                await self.log(
                    f"FORENSIC FLAG [{finding_type}] (confidence: {confidence}): {description}"
                )
                await asyncio.sleep(0.2)

            await self.log(
                f"Image analysis complete — overall risk: {overall_risk}"
            )

        await self.log(
            f"Forensic analysis complete. {total_flags} total flags, "
            f"{high_confidence_flags} high-confidence"
        )

        return {
            "image_analyses": results,
            "total_flags": total_flags,
            "high_confidence_flags": high_confidence_flags,
        }
