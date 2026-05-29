"""Fingerprint Scanner — main orchestrator for IP fingerprinting."""

import asyncio
from .component_extractor import ComponentExtractor
from .listing_comparator import ListingComparator
from .serial_number_analyzer import SerialNumberAnalyzer


class FingerprintScanner:
    """Orchestrates the full IP fingerprinting pipeline."""

    def __init__(self):
        self.extractor = ComponentExtractor()
        self.comparator = ListingComparator()
        self.serial_analyzer = SerialNumberAnalyzer()

    async def scan(self, brand: str, product: str, listings: list[dict],
                   serials: list[str] | None = None,
                   custom_product_data: dict | None = None) -> dict:
        """
        Run full fingerprint scan pipeline.

        1. Extract product DNA
        2. Compare against marketplace listings
        3. Analyze serial numbers (if provided)
        """
        # Step 1: Extract product DNA
        fingerprint = self.extractor.extract(brand, product, custom_product_data)

        # Step 2: Compare listings
        comparison_results = self.comparator.compare(listings, fingerprint)

        # Step 3: Serial analysis
        serial_results = None
        if serials:
            serial_results = self.serial_analyzer.detect_counterfeit_patterns(serials)

        # Calculate overall threat level
        if comparison_results:
            avg_suspicion = sum(
                r["comparison"]["overallSuspicion"] for r in comparison_results
            ) / len(comparison_results)
        else:
            avg_suspicion = 0.0

        high_risk_count = sum(
            1 for r in comparison_results
            if r["comparison"]["verdict"] == "HIGH_RISK"
        )

        threat_level = min(100, int(avg_suspicion * 100 + high_risk_count * 5))

        return {
            "fingerprint": fingerprint,
            "listings_analyzed": len(comparison_results),
            "comparison_results": comparison_results,
            "serial_analysis": serial_results,
            "threat_level": threat_level,
            "high_risk_listings": high_risk_count,
            "summary": self._generate_summary(brand, product, threat_level, high_risk_count, comparison_results),
        }

    def _generate_summary(self, brand: str, product: str, threat: int,
                          high_risk: int, results: list[dict]) -> str:
        """Generate human-readable scan summary."""
        if threat >= 70:
            return (
                f"CRITICAL: {high_risk} high-risk listings detected for {brand} {product}. "
                f"Multiple indicators suggest unauthorized manufacturing. Threat level: {threat}%."
            )
        elif threat >= 40:
            return (
                f"WARNING: Suspicious activity detected for {brand} {product}. "
                f"{high_risk} listing(s) show concerning overlap with genuine product DNA. "
                f"Threat level: {threat}%. Further investigation recommended."
            )
        else:
            return (
                f"LOW RISK: Minimal suspicious activity for {brand} {product}. "
                f"Threat level: {threat}%. Routine monitoring recommended."
            )
