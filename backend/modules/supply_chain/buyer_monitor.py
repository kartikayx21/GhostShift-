"""Buyer Monitor — identifies who else buys from the same suppliers."""

import random
import asyncio


class BuyerMonitor:
    """Monitors supplier buyer lists to find unauthorized purchasers."""

    async def analyze(self, brand: str, product: str, component_data: dict) -> dict:
        """Analyze supplier buyer lists for suspicious overlap."""
        await asyncio.sleep(random.uniform(0.3, 0.8))

        suspicious_buyers = component_data.get("suspicious_buyers", [])
        overlap = component_data.get("overlap_components", 0)
        total = component_data.get("total_components", 5)

        return {
            "chip_id": component_data.get("chip_id", "Unknown"),
            "chip_supplier": component_data.get("chip_supplier", "Unknown"),
            "genuine_buyer": component_data.get("genuine_buyer", brand),
            "suspicious_buyers": suspicious_buyers,
            "overlap_ratio": round(overlap / max(total, 1), 2),
            "risk_level": "high" if overlap >= 3 else "medium" if overlap >= 1 else "low",
            "summary": (
                f"Found {len(suspicious_buyers)} unauthorized buyer(s) purchasing "
                f"{overlap}/{total} of the same components used in genuine {brand} {product}."
            ),
        }
