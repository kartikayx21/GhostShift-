"""Ghost Shift Probability Engine — main scoring model."""

import math


class GhostShiftModel:
    """Weighted probability scoring for ghost shift detection."""

    WEIGHTS = {
        "listingData": 0.20,
        "factoryIntel": 0.25,
        "componentTrace": 0.30,
        "listingForensics": 0.15,
        "pricingAnomaly": 0.10,
    }

    def calculate(self, inputs: dict) -> dict:
        """
        Calculate ghost shift probability from all input signals.

        Args:
            inputs: Dict with keys matching WEIGHTS (listingData, factoryIntel, etc.)
                    Each value should be a score between 0.0 and 1.0.
        """
        scores = {}
        for key in self.WEIGHTS:
            raw = inputs.get(key, 0.0)
            scores[key] = min(1.0, max(0.0, float(raw)))

        # Weighted raw score
        raw_score = sum(scores[k] * self.WEIGHTS[k] for k in self.WEIGHTS)

        # Correlation bonus: if multiple independent signals agree
        correlation_bonus = self._calculate_correlation(scores)

        probability = min(0.99, raw_score + correlation_bonus)

        # Confidence based on data completeness
        data_present = sum(1 for v in scores.values() if v > 0.05)
        confidence = round(data_present / len(self.WEIGHTS), 2)

        # Strongest signal
        primary_signal = max(scores, key=lambda k: scores[k] * self.WEIGHTS[k])

        # Verdict
        if probability > 0.7:
            verdict = "HIGH RISK"
        elif probability > 0.4:
            verdict = "SUSPICIOUS"
        else:
            verdict = "MONITORING"

        return {
            "probability": round(probability, 3),
            "confidence": confidence,
            "breakdown": {k: round(v, 3) for k, v in scores.items()},
            "weights": self.WEIGHTS,
            "weighted_scores": {k: round(scores[k] * self.WEIGHTS[k], 3) for k in self.WEIGHTS},
            "correlation_bonus": round(correlation_bonus, 3),
            "verdict": verdict,
            "primarySignal": primary_signal,
            "primarySignalLabel": self._signal_label(primary_signal),
            "raw_score": round(raw_score, 3),
        }

    def calculate_from_scenario(self, scenario: dict) -> dict:
        """Calculate probability directly from a mock scenario data dict."""
        listings = scenario.get("listings", [])
        factory = scenario.get("factory", {})
        component = scenario.get("component_overlap", {})
        forensics = scenario.get("forensic_analysis", {})
        pricing = scenario.get("pricing_analysis", {})

        # Derive scores from scenario data
        listing_score = min(1.0, len([l for l in listings if l.get("suspicious")]) * 0.25)

        cap_ratio = factory.get("estimated_actual_output", 0) / max(factory.get("declared_capacity", 1), 1)
        factory_score = min(1.0, (cap_ratio - 1.0) * 2) if cap_ratio > 1.0 else factory.get("suspicion_score", 0.3)

        overlap = component.get("overlap_components", 0)
        total = component.get("total_components", 5)
        component_score = overlap / max(total, 1)

        forensic_score = min(1.0, forensics.get("high_confidence_flags", 0) * 0.2)

        pricing_score = pricing.get("geographic_adjustment", 0.5) * (1.0 - pricing.get("price_ratio", 0.5))

        return self.calculate({
            "listingData": listing_score,
            "factoryIntel": factory_score,
            "componentTrace": component_score,
            "listingForensics": forensic_score,
            "pricingAnomaly": pricing_score,
        })

    def _calculate_correlation(self, scores: dict) -> float:
        """Bonus when multiple independent signals agree (above threshold)."""
        threshold = 0.5
        high_signals = sum(1 for v in scores.values() if v > threshold)

        if high_signals >= 4:
            return 0.12
        elif high_signals >= 3:
            return 0.08
        elif high_signals >= 2:
            return 0.04
        return 0.0

    def _signal_label(self, signal_key: str) -> str:
        """Human-readable label for a signal key."""
        labels = {
            "listingData": "Marketplace Intelligence",
            "factoryIntel": "Factory & Employment Intelligence",
            "componentTrace": "Component Supply Chain Tracing",
            "listingForensics": "Listing Forensic Analysis",
            "pricingAnomaly": "Pricing Anomaly Detection",
        }
        return labels.get(signal_key, signal_key)
