import os
import json
import random
import asyncio
import anthropic


class AnthropicClient:
    """Client for Anthropic Claude API with mock mode fallback."""

    def __init__(self):
        self.api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        self.model = os.environ.get(
            "ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"
        )
        # Mock mode when no API key is provided
        self.mock_mode = not bool(self.api_key.strip())
        self._client = None

    def _get_client(self) -> anthropic.AsyncAnthropic:
        """Lazily initialise the async Anthropic client."""
        if self._client is None:
            self._client = anthropic.AsyncAnthropic(api_key=self.api_key)
        return self._client

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

        try:
            client = self._get_client()
            message = await client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
                temperature=0.7,
            )
            return message.content[0].text
        except Exception as e:
            print(f"[WARN] Anthropic API call failed: {e} — falling back to mock mode")
            self.mock_mode = True
            return await self.analyze(system_prompt, user_prompt)

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
            f"image_url, findings (array of {{type, description, confidence}}), overall_risk (0-1).\n"
            f"IMPORTANT: Return ONLY valid JSON, no additional text."
        )

        response = await self.analyze(system_prompt, user_prompt)

        # Try to extract JSON from the response
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Attempt to find JSON array in the response
            try:
                start = response.index("[")
                end = response.rindex("]") + 1
                return json.loads(response[start:end])
            except (ValueError, json.JSONDecodeError):
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

            # Weighted risk calculation (scaled down to prevent hitting 100% ceiling)
            risk_score = min(
                98.0,
                (suspicious_listings * 4)
                + (suspicious_buyers * 5)
                + (suspicious_signals * 4)
                + (forensic_flags * 3)
                + random.uniform(2, 8),
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

            # Extract real deep-link URLs from agent findings
            listing_url = ""
            suspicious_list = hunter_findings.get("suspicious_listings", [])
            if suspicious_list:
                first_listing = suspicious_list[0]
                listing_url = first_listing.get("url", "")
                # Build detailed listing descriptions with individual URLs
                listing_details = []
                for sl in suspicious_list[:5]:
                    title = sl.get("title", "Unknown")
                    platform = sl.get("platform", "Unknown")
                    price = sl.get("price", 0)
                    url = sl.get("url", "")
                    listing_details.append(f"{title} (${price}) on {platform}")

            supplier_url = ""
            suppliers = component_findings.get("suppliers", [])
            if suppliers:
                # Find supplier with suspicious buyers
                for sup in suppliers:
                    buyers = sup.get("known_buyers", [])
                    if any(b.get("suspicious") for b in buyers):
                        supplier_url = sup.get("source_url", "")
                        break
                if not supplier_url:
                    supplier_url = suppliers[0].get("source_url", "")

            employment_url = ""
            employee_data = factory_findings.get("employee_movements", [])
            if employee_data:
                employment_url = employee_data[0].get("linkedin_url", "")
            if not employment_url:
                job_data = factory_findings.get("job_postings", [])
                if job_data:
                    employment_url = job_data[0].get("source_url", "")

            evidence = [
                {
                    "type": "listing",
                    "description": f"Found {suspicious_listings} suspicious marketplace listings with prices 40-78% below retail across AliExpress, DHgate, and Taobao",
                    "source_url": listing_url,
                    "confidence": 0.87,
                },
                {
                    "type": "supplier",
                    "description": f"Identified {suspicious_buyers} suspicious entities purchasing identical components from {brand}'s verified suppliers",
                    "source_url": supplier_url,
                    "confidence": 0.78,
                },
                {
                    "type": "employment",
                    "description": f"Detected {suspicious_signals} employee movements from {brand} to suspected counterfeit manufacturers in Shenzhen/Guangzhou corridor",
                    "source_url": employment_url,
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
            f"Provide your verdict as a JSON object.\n"
            f"IMPORTANT: Return ONLY valid JSON, no additional text."
        )

        response = await self.analyze(system_prompt, user_prompt)

        # Try to extract JSON from the response
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Attempt to find JSON object in the response
            try:
                start = response.index("{")
                end = response.rindex("}") + 1
                return json.loads(response[start:end])
            except (ValueError, json.JSONDecodeError):
                return {
                    "risk_score": 50.0,
                    "verdict": response,
                    "evidence": [],
                    "recommended_action": "Investigate Further",
                }


# Singleton instance
llm = AnthropicClient()
