"""Price Threshold Model — 'Too cheap' detection for listing forensics."""


class PriceThresholdModel:
    """Detects impossibly cheap pricing that indicates counterfeiting."""

    # Geographic adjustment factors (shipping + customs + margin)
    GEO_FACTORS = {
        "CN→US": 0.92, "CN→EU": 0.88, "CN→UK": 0.90,
        "CN→HK": 0.97, "CN→JP": 0.91, "CN→AU": 0.87,
    }

    # BOM cost estimates by product category (% of retail)
    BOM_ESTIMATES = {
        "wireless_earbuds": 0.25,
        "smartphone": 0.35,
        "vacuum": 0.30,
        "smartwatch": 0.28,
        "default": 0.30,
    }

    def analyze(self, listing_price: float, genuine_price: float,
                components: list[str] | None = None,
                product_category: str = "default",
                shipping_route: str = "CN→US") -> dict:
        """
        Calculate pricing suspicion score.

        Returns thresholds, BOM analysis, and adjusted suspicion.
        """
        if genuine_price <= 0:
            return {"error": "Invalid genuine price"}

        ratio = listing_price / genuine_price
        bom_pct = self.BOM_ESTIMATES.get(product_category, 0.30)
        bom_estimate = genuine_price * bom_pct
        below_bom = listing_price < bom_estimate
        geo_factor = self.GEO_FACTORS.get(shipping_route, 0.90)

        # Base suspicion from price ratio
        if ratio < 0.25:
            base_suspicion = 0.98
        elif ratio < 0.40:
            base_suspicion = 0.85
        elif ratio < 0.60:
            base_suspicion = 0.65
        elif ratio < 0.85:
            base_suspicion = 0.30
        else:
            base_suspicion = 0.08

        # Adjust for geography
        adjusted_suspicion = round(base_suspicion * geo_factor, 2)

        # Determine threshold zone
        if ratio > 0.85:
            threshold = "green"
            label = "Normal discount range"
        elif ratio > 0.60:
            threshold = "yellow"
            label = "Suspicious pricing"
        else:
            threshold = "red"
            label = "Impossible without corner-cutting"

        return {
            "listing_price": listing_price,
            "genuine_price": genuine_price,
            "price_ratio": round(ratio, 3),
            "estimated_bom_cost": round(bom_estimate, 2),
            "below_bom_cost": below_bom,
            "threshold": threshold,
            "threshold_label": label,
            "thresholds": {
                "green": {"min_ratio": 0.85, "label": "Normal discount"},
                "yellow": {"min_ratio": 0.60, "label": "Suspicious"},
                "red": {"min_ratio": 0.0, "label": "Impossible pricing"},
            },
            "base_suspicion": round(base_suspicion, 2),
            "geographic_adjustment": geo_factor,
            "adjusted_suspicion": adjusted_suspicion,
            "shipping_route": shipping_route,
            "product_category": product_category,
        }

    def analyze_batch(self, listings: list[dict], genuine_price: float,
                      product_category: str = "default") -> dict:
        """Analyze pricing across multiple listings."""
        results = []
        for listing in listings:
            price = listing.get("price", 0)
            result = self.analyze(price, genuine_price, product_category=product_category)
            results.append({**listing, "pricing_analysis": result})

        red_count = sum(1 for r in results if r["pricing_analysis"]["threshold"] == "red")
        yellow_count = sum(1 for r in results if r["pricing_analysis"]["threshold"] == "yellow")
        avg_ratio = (
            sum(r["pricing_analysis"]["price_ratio"] for r in results) / max(len(results), 1)
        )

        return {
            "listings_analyzed": len(results),
            "results": results,
            "red_zone_count": red_count,
            "yellow_zone_count": yellow_count,
            "average_price_ratio": round(avg_ratio, 3),
            "below_bom_count": sum(1 for r in results if r["pricing_analysis"]["below_bom_cost"]),
        }
