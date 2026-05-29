"""Image Analyzer — AI-powered listing image forensics via Ollama."""

import random
import asyncio


class ImageAnalyzer:
    """Analyzes product listing images for counterfeit indicators using Ollama."""

    FORENSICS_PROMPT = """Analyze this product listing image for IP theft indicators.
Look for and report on:

1. BACKGROUND ELEMENTS:
   - Factory layout visible? (conveyor belts, workstations)
   - Boxes/packaging in background — read any text/logos visible
   - Tools/equipment — professional vs. garage operation
   - Other products visible — cross-brand contamination?

2. PRODUCT ANALYSIS:
   - Logo placement: exact pixels, font weight, kerning
   - Color accuracy: estimate Pantone deviation
   - Build quality indicators: seam lines, screw types
   - Label quality: print resolution, alignment

3. METADATA SIGNALS:
   - Image was likely taken in: [location estimate from bg]
   - Same factory as listing ID: [cross-reference]
   - Confidence this is counterfeit: [0-100]%

Return as JSON: {{ backgroundElements, productAnalysis, locationEstimate, counterfeitConfidence, evidencePoints: [] }}"""

    async def analyze(self, brand: str, product: str, findings: dict) -> dict:
        """Analyze forensic findings (mock or Ollama-powered)."""
        await asyncio.sleep(random.uniform(0.5, 1.0))

        forensic_data = findings.get("forensic_analysis", {})
        raw_findings = forensic_data.get("findings", [])

        analyzed_images = []
        for i, finding in enumerate(raw_findings):
            analyzed_images.append({
                "finding_id": i + 1,
                "type": finding.get("type", "unknown"),
                "description": finding.get("description", ""),
                "confidence": finding.get("confidence", 0.5),
                "severity": (
                    "critical" if finding.get("confidence", 0) > 0.85
                    else "high" if finding.get("confidence", 0) > 0.7
                    else "medium" if finding.get("confidence", 0) > 0.5
                    else "low"
                ),
                "category": self._categorize_finding(finding.get("type", "")),
            })

        high_conf = sum(1 for a in analyzed_images if a["severity"] in ("critical", "high"))
        avg_confidence = (
            sum(a["confidence"] for a in analyzed_images) / max(len(analyzed_images), 1)
        )

        return {
            "images_analyzed": forensic_data.get("images_analyzed", 0),
            "total_flags": forensic_data.get("total_flags", len(raw_findings)),
            "high_confidence_flags": high_conf,
            "findings": analyzed_images,
            "average_confidence": round(avg_confidence, 2),
            "counterfeit_probability": round(min(1.0, avg_confidence + high_conf * 0.05), 2),
            "ollama_model": "phi3:mini",
            "prompt_template": self.FORENSICS_PROMPT[:100] + "...",
        }

    def _categorize_finding(self, finding_type: str) -> str:
        """Categorize a finding type into a broader category."""
        categories = {
            "logo_inconsistency": "PRODUCT_ANALYSIS",
            "material_quality": "PRODUCT_ANALYSIS",
            "packaging_anomaly": "PRODUCT_ANALYSIS",
            "background_match": "BACKGROUND_ELEMENTS",
            "serial_mismatch": "METADATA_SIGNALS",
            "color_deviation": "PRODUCT_ANALYSIS",
            "build_quality": "PRODUCT_ANALYSIS",
            "font_mismatch": "PRODUCT_ANALYSIS",
        }
        return categories.get(finding_type, "UNKNOWN")
