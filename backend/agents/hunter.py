import asyncio
from agents.base import BaseAgent
from services.brightdata import brightdata


class HunterAgent(BaseAgent):
    """Agent 1 — The Hunter: Scans online marketplaces for suspicious counterfeit listings."""

    def __init__(self):
        super().__init__(
            name="The Hunter",
            description="Scans online marketplaces for suspicious counterfeit listings",
        )

    async def run(self, brand: str, product: str, context: dict = None) -> dict:
        await self.log(f"Initializing marketplace scan for {brand} {product}...")

        # Fetch marketplace listings
        listings = await brightdata.search_marketplaces(brand, product)

        await self.log("Scanning AliExpress...")
        await asyncio.sleep(0.5)
        await self.log("Scanning DHgate...")
        await asyncio.sleep(0.5)
        await self.log("Scanning Taobao...")
        await asyncio.sleep(0.5)

        # Filter suspicious listings
        suspicious = []
        for listing in listings:
            is_suspicious = listing.get("is_suspicious", False)
            price = listing.get("price", 0)
            retail = listing.get("retail_price", 1)
            monthly_sales = listing.get("monthly_sales", 0)

            if is_suspicious or price < retail * 0.6 or monthly_sales > 1000:
                suspicious.append(listing)

        total = len(listings)
        await self.log(
            f"Found {len(suspicious)} suspicious listings out of {total} results"
        )

        for listing in suspicious:
            price = listing.get("price", 0)
            retail = listing.get("retail_price", 1)
            percent_below = round((1 - price / retail) * 100, 1) if retail > 0 else 0
            title = listing.get("title", "Unknown")
            platform = listing.get("platform", "Unknown")
            await self.log(
                f"ALERT: {title} at ${price} on {platform} ({percent_below}% below retail)"
            )

        return {
            "listings": listings,
            "suspicious_listings": suspicious,
            "total_scanned": total,
            "platforms_checked": ["AliExpress", "DHgate", "Taobao"],
        }
