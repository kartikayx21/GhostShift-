"""Knowledge Transfer Detector — correlates employee movements with factory output."""

import random
import asyncio


class KnowledgeTransferDetector:
    """Detects suspicious talent movement patterns indicating IP knowledge transfer."""

    async def analyze(self, employee_results: dict, factory_data: dict) -> dict:
        """Correlate employee movements with factory capability changes."""
        await asyncio.sleep(random.uniform(0.2, 0.5))

        movements = employee_results.get("results", [])
        critical = employee_results.get("critical_transfers", 0)
        high = employee_results.get("high_transfers", 0)

        # Cross-reference with factory capacity
        factory_capacity = factory_data.get("estimated_actual_output", 0)
        declared_capacity = factory_data.get("declared_capacity", 0)
        capacity_ratio = factory_capacity / max(declared_capacity, 1)

        # Knowledge transfer probability
        kt_probability = min(1.0, (critical * 0.3 + high * 0.15 + (capacity_ratio - 1.0) * 0.2))

        correlations = []
        for m in movements:
            if m.get("classification") in ("CRITICAL", "HIGH"):
                correlations.append({
                    "employee": m.get("name", "Unknown"),
                    "signal": m.get("risk_signal", ""),
                    "from": m.get("previous_employer", ""),
                    "to": m.get("current_employer", ""),
                    "correlation": "Factory output increased within 3 months of transfer" if capacity_ratio > 1.2 else "Monitoring",
                })

        return {
            "kt_probability": round(max(0, kt_probability), 2),
            "capacity_anomaly": capacity_ratio > 1.3,
            "capacity_ratio": round(capacity_ratio, 2),
            "correlations": correlations,
            "risk_level": "high" if kt_probability > 0.6 else "medium" if kt_probability > 0.3 else "low",
            "summary": (
                f"Detected {len(correlations)} knowledge transfer correlation(s). "
                f"Factory operating at {int(capacity_ratio * 100)}% of declared capacity."
            ),
        }
