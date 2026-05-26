import asyncio
from agents.base import BaseAgent
from services.brightdata import brightdata


class ComponentTracerAgent(BaseAgent):
    """Agent 2 — The Component Tracer: Traces supply chain for diverted components."""

    def __init__(self):
        super().__init__(
            name="The Component Tracer",
            description="Traces component supply chains to identify diversion to counterfeiters",
        )

    async def run(self, brand: str, product: str, context: dict = None) -> dict:
        components = [
            "LCD display panel",
            "lithium battery cell",
            "custom IC chip",
            "injection molded casing",
        ]

        await self.log(f"Tracing component supply chain for {brand} {product}...")
        await asyncio.sleep(0.3)

        suppliers = await brightdata.search_suppliers(brand, product, components)

        suspicious_buyers = []

        for supplier in suppliers:
            supplier_name = supplier.get("supplier_name", "Unknown")
            components_list = supplier.get("components_supplied", [])
            await self.log(
                f"Traced supplier: {supplier_name} — supplies {', '.join(components_list)}"
            )
            await asyncio.sleep(0.3)

            for buyer in supplier.get("known_buyers", []):
                if buyer.get("suspicious", False):
                    buyer_name = buyer.get("name", "Unknown")
                    suspicious_buyers.append(
                        {
                            "buyer_name": buyer_name,
                            "supplier": supplier_name,
                            "components": components_list,
                        }
                    )
                    await self.log(
                        f"WARNING: Suspicious buyer '{buyer_name}' purchasing "
                        f"{', '.join(components_list)} from {supplier_name}"
                    )

        await self.log(
            f"Supply chain trace complete. Identified {len(suspicious_buyers)} suspicious buyers"
        )

        return {
            "suppliers": suppliers,
            "suspicious_buyers": suspicious_buyers,
            "components_traced": components,
        }
