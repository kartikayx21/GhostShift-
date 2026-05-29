"""Employee Tracker — LinkedIn/Glassdoor movement analysis."""

import random
import asyncio


class EmployeeTracker:
    """Tracks employee movements between legitimate manufacturers and unknown factories."""

    RISK_SIGNALS = {
        "suspicious_transfer": {
            "condition": "NDA_role → unknown_factory < 6_months",
            "risk_weight": 0.85,
        },
        "knowledge_transfer": {
            "condition": "same_role + same_product_category",
            "risk_weight": 0.90,
        },
        "mass_exodus": {
            "condition": "3+ employees from same dept within 6 months",
            "risk_weight": 0.95,
        },
    }

    async def analyze(self, brand: str, product: str, movements: list[dict]) -> dict:
        """Analyze employee movements for knowledge transfer risk."""
        await asyncio.sleep(random.uniform(0.3, 0.8))

        analyzed = []
        total_risk = 0.0

        for movement in movements:
            risk_weight = movement.get("risk_weight", 0.5)
            months = movement.get("months_since_transfer", 12)

            # Recency factor: more recent = higher risk
            recency_factor = max(0.3, 1.0 - (months / 24))
            adjusted_risk = round(risk_weight * recency_factor, 2)
            total_risk += adjusted_risk

            analyzed.append({
                **movement,
                "adjusted_risk": adjusted_risk,
                "recency_factor": round(recency_factor, 2),
                "classification": (
                    "CRITICAL" if adjusted_risk > 0.8 else
                    "HIGH" if adjusted_risk > 0.6 else
                    "MEDIUM" if adjusted_risk > 0.3 else "LOW"
                ),
            })

        avg_risk = round(total_risk / max(len(movements), 1), 2)

        return {
            "movements_analyzed": len(analyzed),
            "results": analyzed,
            "average_risk": avg_risk,
            "critical_transfers": sum(1 for a in analyzed if a["classification"] == "CRITICAL"),
            "high_transfers": sum(1 for a in analyzed if a["classification"] == "HIGH"),
            "risk_signals_checked": self.RISK_SIGNALS,
            "api_used": "SCRAPING_BROWSER",
            "targets": ["linkedin.com", "glassdoor.com", "apollo.io"],
            "risk_level": "high" if avg_risk > 0.6 else "medium" if avg_risk > 0.3 else "low",
        }
