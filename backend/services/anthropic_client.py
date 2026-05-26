import os
import json
import random
import asyncio
import anthropic


class AnthropicClient:
    """Client for Claude AI analysis with mock mode fallback."""

    def __init__(self):
        self.api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        self.mock_mode = not bool(self.api_key.strip())
        self.client = None
        if not self.mock_mode:
            self.client = anthropic.Anthropic(api_key=self.api_key)

    async def analyze(self, system_prompt: str, user_prompt: str) -> str:
        """General-purpose analysis using Claude."""
        if self.mock_mode:
            await asyncio.sleep(random.uniform(1.0, 2.0))
            return (
                "Based on the available intelligence data, there are multiple indicators "
                "suggesting unauthorized production activity. The convergence of suspicious "
                "marketplace listings, supply chain anomalies, and employee movements between "
                "the legitimate manufacturer and unknown entities creates a pattern consistent "
                "with ghost shift operations. Further investigation is recommended to confirm "
                "the scope and scale of potential IP theft."
            )

        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return message.content[0].text

    async def analyze_forensics(
        self, image_descriptions: list[dict], brand: str, product: str
    ) -> list[dict]:
        """Analyze product images for counterfeit indicators."""
        if self.mock_mode:
            await asyncio.sleep(random.uniform(1.5, 2.5))
            results = []
            for img in image_descriptions:
                risk = random.uniform(0.5, 0.95)
                findings = [
                    {
                        "type": "logo_inconsistency",
                        "description": f"Logo font kerning on {brand} branding differs by 0.3mm from authentic samples. Character spacing is inconsistent with official brand guidelines.",
                        "confidence": round(random.uniform(0.7, 0.95), 2),
                    },
                    {
                        "type": "material_quality",
                        "description": f"Surface finish on {product} casing shows injection molding artifacts not present in genuine units. Parting line visible along side panel.",
                        "confidence": round(random.uniform(0.6, 0.85), 2),
                    },
                    {
                        "type": "packaging_anomaly",
                        "description": f"Packaging QR code pattern uses older {brand} format deprecated in 2025. Holographic seal shows moiré pattern inconsistency.",
                        "confidence": round(random.uniform(0.55, 0.80), 2),
                    },
                ]
                results.append(
                    {
                        "image_url": img.get("url", ""),
                        "findings": random.sample(findings, k=random.randint(1, 3)),
                        "overall_risk": round(risk, 2),
                    }
                )
            return results

        # Real mode: construct prompt describing images and ask Claude for analysis
        image_text = "\n".join(
            [
                f"Image {i+1}: From {img.get('source_platform', 'unknown')} - "
                f"'{img.get('listing_title', 'No title')}' (URL: {img.get('url', '')})"
                for i, img in enumerate(image_descriptions)
            ]
        )

        system_prompt = (
            "You are a forensic product authentication expert. Analyze product images "
            "for signs of counterfeiting. Look for: logo inconsistencies, material quality "
            "issues, packaging anomalies, font/typography differences, color mismatches, "
            "and any other indicators of non-genuine products. Return your analysis as JSON."
        )

        user_prompt = (
            f"Analyze these product images for {brand} {product} authenticity:\n\n"
            f"{image_text}\n\n"
            f"For each image, provide findings as JSON array with objects containing: "
            f"image_url, findings (array of {{type, description, confidence}}), overall_risk (0-1)."
        )

        response = await self.analyze(system_prompt, user_prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return [
                {
                    "image_url": img.get("url", ""),
                    "findings": [
                        {
                            "type": "analysis_error",
                            "description": "Could not parse forensic analysis results",
                            "confidence": 0.0,
                        }
                    ],
                    "overall_risk": 0.5,
                }
                for img in image_descriptions
            ]

    async def synthesize_verdict(
        self, brand: str, product: str, all_findings: dict
    ) -> dict:
        """Synthesize all agent findings into a final verdict."""
        if self.mock_mode:
            await asyncio.sleep(random.uniform(1.5, 2.5))

            # Compute risk based on findings from all agents
            hunter_findings = all_findings.get("hunter", {})
            component_findings = all_findings.get("component_tracer", {})
            factory_findings = all_findings.get("factory_spy", {})
            forensics_findings = all_findings.get("forensics", {})

            suspicious_listings = len(
                hunter_findings.get("suspicious_listings", [])
            )
            suspicious_buyers = len(
                component_findings.get("suspicious_buyers", [])
            )
            suspicious_signals = factory_findings.get("suspicious_signals", 0)
            forensic_flags = forensics_findings.get("total_flags", 0)

            # Weighted risk calculation
            risk_score = min(
                100.0,
                (suspicious_listings * 12)
                + (suspicious_buyers * 15)
                + (suspicious_signals * 10)
                + (forensic_flags * 8)
                + random.uniform(5, 15),
            )
            risk_score = round(risk_score, 1)

            if risk_score >= 75:
                recommended_action = "Report"
                verdict_text = (
                    f"HIGH RISK: Strong evidence of ghost shift operations targeting {brand} {product}. "
                    f"Multiple corroborating signals detected across marketplace listings, supply chain "
                    f"diversion, employee movements, and forensic product analysis. Immediate action recommended."
                )
            elif risk_score >= 40:
                recommended_action = "Investigate Further"
                verdict_text = (
                    f"MEDIUM RISK: Moderate indicators of potential unauthorized production of {brand} {product}. "
                    f"Some suspicious marketplace activity and supply chain anomalies detected, but insufficient "
                    f"evidence for definitive conclusion. Additional monitoring and deeper investigation advised."
                )
            else:
                recommended_action = "Low Risk"
                verdict_text = (
                    f"LOW RISK: Limited indicators of counterfeit {brand} {product} activity detected. "
                    f"Minor marketplace anomalies may represent authorized grey market activity. "
                    f"Routine monitoring recommended."
                )

            evidence = [
                {
                    "type": "listing",
                    "description": f"Found {suspicious_listings} suspicious marketplace listings with prices 40-78% below retail across AliExpress, DHgate, and Taobao",
                    "source_url": "https://aliexpress.com",
                    "confidence": 0.87,
                },
                {
                    "type": "supplier",
                    "description": f"Identified {suspicious_buyers} suspicious entities purchasing identical components from {brand}'s verified suppliers",
                    "source_url": "https://1688.com",
                    "confidence": 0.78,
                },
                {
                    "type": "employment",
                    "description": f"Detected {suspicious_signals} employee movements from {brand} to suspected counterfeit manufacturers in Shenzhen/Guangzhou corridor",
                    "source_url": "https://linkedin.com",
                    "confidence": 0.72,
                },
                {
                    "type": "forensic",
                    "description": f"AI forensic analysis flagged {forensic_flags} product image anomalies including logo inconsistencies and material quality differences",
                    "source_url": "",
                    "confidence": 0.82,
                },
                {
                    "type": "synthesis",
                    "description": f"Cross-referencing all intelligence streams reveals a coordinated pattern consistent with organized ghost shift operation targeting {brand} {product}",
                    "source_url": "",
                    "confidence": round(risk_score / 100, 2),
                },
            ]

            return {
                "risk_score": risk_score,
                "verdict": verdict_text,
                "evidence": evidence,
                "recommended_action": recommended_action,
            }

        # Real mode: send comprehensive analysis prompt to Claude
        system_prompt = (
            "You are the lead intelligence analyst for a counterfeit product investigation. "
            "Your role is to synthesize findings from multiple investigation agents and produce "
            "a definitive verdict. You must return a JSON object with: risk_score (0-100), "
            "verdict (detailed text explanation), evidence (array of {type, description, source_url, confidence}), "
            "and recommended_action ('Report', 'Investigate Further', or 'Low Risk')."
        )

        user_prompt = (
            f"Synthesize these investigation findings for {brand} {product}:\n\n"
            f"**Marketplace Intelligence (The Hunter):**\n{json.dumps(all_findings.get('hunter', {}), indent=2)}\n\n"
            f"**Supply Chain Analysis (Component Tracer):**\n{json.dumps(all_findings.get('component_tracer', {}), indent=2)}\n\n"
            f"**Employment Intelligence (Factory Spy):**\n{json.dumps(all_findings.get('factory_spy', {}), indent=2)}\n\n"
            f"**Forensic Analysis (Forensics Agent):**\n{json.dumps(all_findings.get('forensics', {}), indent=2)}\n\n"
            f"Provide your verdict as a JSON object."
        )

        response = await self.analyze(system_prompt, user_prompt)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "risk_score": 50.0,
                "verdict": response,
                "evidence": [],
                "recommended_action": "Investigate Further",
            }


# Singleton instance
claude = AnthropicClient()
