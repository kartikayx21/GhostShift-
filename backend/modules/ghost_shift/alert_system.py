"""Alert System — threshold-based notifications for ghost shift detection."""


class AlertSystem:
    """Generates alerts based on ghost shift probability thresholds."""

    THRESHOLDS = {
        "critical": {"min": 0.80, "label": "CRITICAL", "color": "#ef4444", "action": "Immediate enforcement"},
        "warning": {"min": 0.50, "label": "WARNING", "color": "#f59e0b", "action": "Escalate investigation"},
        "watch": {"min": 0.30, "label": "WATCH", "color": "#3b82f6", "action": "Enhanced monitoring"},
        "clear": {"min": 0.0, "label": "CLEAR", "color": "#22c55e", "action": "Routine monitoring"},
    }

    def evaluate(self, probability: float, scenario_name: str = "",
                 brand: str = "", product: str = "") -> dict:
        """Evaluate probability against thresholds and generate alert."""
        alert_level = "clear"
        for level, config in self.THRESHOLDS.items():
            if probability >= config["min"]:
                alert_level = level
                break

        config = self.THRESHOLDS[alert_level]

        return {
            "level": config["label"],
            "color": config["color"],
            "probability": round(probability, 3),
            "action": config["action"],
            "message": self._build_message(alert_level, probability, brand, product),
            "scenario": scenario_name,
            "notification": {
                "title": f"Ghost Shift Alert: {config['label']}",
                "body": f"{brand} {product} — {probability*100:.0f}% probability of unauthorized manufacturing",
                "urgency": alert_level,
            },
        }

    def _build_message(self, level: str, prob: float, brand: str, product: str) -> str:
        """Generate alert message."""
        messages = {
            "critical": f"CRITICAL: {prob*100:.0f}% probability of ghost shift targeting {brand} {product}. Multiple corroborating signals confirmed. Immediate action required.",
            "warning": f"WARNING: {prob*100:.0f}% probability detected for {brand} {product}. Suspicious activity across multiple intelligence streams. Escalation recommended.",
            "watch": f"WATCH: {prob*100:.0f}% probability for {brand} {product}. Some suspicious signals detected. Enhanced monitoring activated.",
            "clear": f"CLEAR: {prob*100:.0f}% probability for {brand} {product}. No significant threats detected. Routine monitoring continues.",
        }
        return messages.get(level, "Unknown alert level")
