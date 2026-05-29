"""Listing Comparator — compares marketplace listings against genuine product fingerprint."""

import random


class ListingComparator:
    """Compares scraped listings against known genuine product DNA."""

    def compare(self, listings: list[dict], fingerprint: dict) -> list[dict]:
        """
        Compare each listing against the genuine product fingerprint.

        Returns listings enriched with comparison scores.
        """
        results = []
        genuine_chips = set(fingerprint.get("componentSignature", {}).get("chipIds", []))

        for listing in listings:
            component_score = self._score_component_overlap(listing, genuine_chips)
            visual_score = self._score_visual_match(listing, fingerprint.get("visualFingerprint", {}))
            price_score = self._score_pricing(listing)

            overall = round(
                component_score * 0.40 + visual_score * 0.35 + price_score * 0.25, 2
            )

            results.append({
                **listing,
                "comparison": {
                    "componentOverlap": round(component_score, 2),
                    "visualMatch": round(visual_score, 2),
                    "pricingDeviation": round(price_score, 2),
                    "overallSuspicion": overall,
                    "verdict": (
                        "HIGH_RISK" if overall > 0.7
                        else "SUSPICIOUS" if overall > 0.4
                        else "LOW_RISK"
                    ),
                },
            })

        return sorted(results, key=lambda x: x["comparison"]["overallSuspicion"], reverse=True)

    def _score_component_overlap(self, listing: dict, genuine_chips: set) -> float:
        """Score based on component/chip mention overlap."""
        title = (listing.get("title", "") + " " + listing.get("description", "")).lower()
        if not genuine_chips:
            return 0.5

        matches = sum(1 for chip in genuine_chips if chip.lower() in title)
        if matches > 0:
            return min(1.0, 0.6 + matches * 0.15)

        # Check for generic suspicious indicators
        suspicious_terms = ["1:1", "aaa+", "original quality", "factory direct", "same as genuine"]
        for term in suspicious_terms:
            if term in title:
                return random.uniform(0.5, 0.8)

        return random.uniform(0.1, 0.4)

    def _score_visual_match(self, listing: dict, visual_fp: dict) -> float:
        """Score visual similarity (mock — would use CV in production)."""
        flags = listing.get("flags", [])
        if "logo_inconsistency" in flags or "background_packaging_visible" in flags:
            return random.uniform(0.6, 0.9)
        if listing.get("suspicious", False):
            return random.uniform(0.4, 0.7)
        return random.uniform(0.05, 0.3)

    def _score_pricing(self, listing: dict) -> float:
        """Score pricing anomaly (lower price = higher suspicion)."""
        price = listing.get("price", 0)
        genuine = listing.get("genuine_price", 0)
        if genuine <= 0:
            return 0.5

        ratio = price / genuine
        if ratio < 0.25:
            return 0.95  # Impossibly cheap
        elif ratio < 0.40:
            return 0.85  # Below BOM
        elif ratio < 0.60:
            return 0.65  # Suspicious
        elif ratio < 0.85:
            return 0.30  # Gray market possible
        return 0.10  # Normal range
