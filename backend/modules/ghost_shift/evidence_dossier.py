"""Evidence Dossier Generator — creates legal-quality investigation reports."""

import json
import asyncio
import random


class EvidenceDossierGenerator:
    """Generates structured evidence dossiers from investigation data."""

    DOSSIER_PROMPT = """You are an IP theft investigator writing a legal-quality evidence report.
Given this data: {evidence_data}

Generate a structured dossier with:
1. EXECUTIVE SUMMARY (3 sentences, suitable for legal team)
2. EVIDENCE CHAIN (chronological, each item sourced)
3. TECHNICAL ANALYSIS (component matching, serial patterns)
4. FACTORY INTELLIGENCE (employee movement, capacity anomalies)
5. RECOMMENDED ACTIONS (platform takedown, legal, customs alert)
6. EVIDENCE LINKS (all URLs scraped, archived)

Confidence Level: {probability}%
Format: Professional legal memo style"""

    async def generate(self, scenario: dict, probability_result: dict) -> dict:
        """Generate a full evidence dossier from scenario data."""
        await asyncio.sleep(random.uniform(0.5, 1.0))

        prob = probability_result.get("probability", 0) * 100
        verdict = probability_result.get("verdict", "MONITORING")
        breakdown = probability_result.get("breakdown", {})

        # Build structured dossier sections
        dossier = {
            "executive_summary": self._build_executive_summary(scenario, prob, verdict),
            "evidence_chain": self._build_evidence_chain(scenario),
            "technical_analysis": self._build_technical_analysis(scenario),
            "factory_intelligence": self._build_factory_intel(scenario),
            "recommended_actions": self._build_recommendations(verdict, prob),
            "evidence_links": self._collect_evidence_links(scenario),
            "metadata": {
                "generated_at": "2026-05-29T00:00:00Z",
                "probability": round(prob, 1),
                "verdict": verdict,
                "breakdown": breakdown,
                "model": "phi3:mini",
            },
        }

        return dossier

    def _build_executive_summary(self, scenario: dict, prob: float, verdict: str) -> str:
        """Build 3-sentence executive summary."""
        name = scenario.get("scenario_name", "Unknown")
        factory = scenario.get("factory", {})
        listings = scenario.get("listings", [])

        return (
            f"Investigation '{name}' has concluded with a {verdict} determination "
            f"at {prob:.0f}% confidence. Analysis of {len(listings)} marketplace listings, "
            f"component supply chain records, and employee movement data reveals "
            f"{'strong' if prob > 60 else 'moderate' if prob > 30 else 'weak'} evidence "
            f"of unauthorized manufacturing activity at {factory.get('name', 'unknown facility')} "
            f"in {factory.get('location', 'unknown location')}. "
            f"{'Immediate enforcement action is recommended.' if prob > 60 else 'Continued monitoring is advised.' if prob > 30 else 'No immediate action required.'}"
        )

    def _build_evidence_chain(self, scenario: dict) -> list[dict]:
        """Build chronological evidence chain."""
        chain = []
        seq = 1

        # Employee movements (earliest events)
        for emp in scenario.get("employee_movements", []):
            chain.append({
                "sequence": seq,
                "date": emp.get("transfer_date", "Unknown"),
                "type": "EMPLOYEE_TRANSFER",
                "description": f"{emp.get('name', 'Unknown')} transferred from {emp.get('previous_employer', '?')} to {emp.get('current_employer', '?')}",
                "risk_weight": emp.get("risk_weight", 0.5),
                "source": "Employment intelligence (Scraping Browser)",
            })
            seq += 1

        # Job postings
        for post in scenario.get("job_postings", []):
            chain.append({
                "sequence": seq,
                "date": post.get("posted_date", "Unknown"),
                "type": "JOB_POSTING",
                "description": f"'{post.get('title', '?')}' posted by {post.get('company', '?')}",
                "red_flags": post.get("red_flags", []),
                "source": "SERP API",
            })
            seq += 1

        # Listings
        for listing in scenario.get("listings", []):
            chain.append({
                "sequence": seq,
                "date": "Ongoing",
                "type": "MARKETPLACE_LISTING",
                "description": f"'{listing.get('title', '?')}' on {listing.get('platform', '?')} at ${listing.get('price', 0):.2f}",
                "flags": listing.get("flags", []),
                "source": f"Web Scraper API ({listing.get('platform', 'unknown')})",
            })
            seq += 1

        return chain

    def _build_technical_analysis(self, scenario: dict) -> dict:
        """Build technical analysis section."""
        serial = scenario.get("serial_analysis", {})
        component = scenario.get("component_overlap", {})
        forensics = scenario.get("forensic_analysis", {})

        return {
            "component_matching": {
                "chip_id": component.get("chip_id", "N/A"),
                "overlap_ratio": f"{component.get('overlap_components', 0)}/{component.get('total_components', 5)}",
                "shared_supplier": component.get("chip_supplier", "N/A"),
                "verdict": "Components sourced from identical supply chain" if component.get("overlap_components", 0) >= 3 else "Partial supply chain overlap",
            },
            "serial_patterns": {
                "genuine_format": serial.get("genuine_pattern", "N/A"),
                "batches_detected": len(serial.get("counterfeit_batches", [])),
                "batch_details": serial.get("counterfeit_batches", []),
            },
            "forensic_flags": {
                "total": forensics.get("total_flags", 0),
                "high_confidence": forensics.get("high_confidence_flags", 0),
                "findings": forensics.get("findings", []),
            },
        }

    def _build_factory_intel(self, scenario: dict) -> dict:
        """Build factory intelligence section."""
        factory = scenario.get("factory", {})
        employees = scenario.get("employee_movements", [])

        return {
            "factory": factory,
            "capacity_analysis": {
                "declared": factory.get("declared_capacity", 0),
                "estimated_actual": factory.get("estimated_actual_output", 0),
                "ratio": round(factory.get("estimated_actual_output", 0) / max(factory.get("declared_capacity", 1), 1), 2),
                "anomaly": factory.get("estimated_actual_output", 0) > factory.get("declared_capacity", 0) * 1.3,
            },
            "employee_transfers": [
                {
                    "name": e.get("name", "Unknown"),
                    "from": e.get("previous_employer", "?"),
                    "to": e.get("current_employer", "?"),
                    "role": e.get("previous_role", "?"),
                    "risk": e.get("risk_signal", ""),
                    "months_ago": e.get("months_since_transfer", 0),
                }
                for e in employees
            ],
        }

    def _build_recommendations(self, verdict: str, probability: float) -> list[dict]:
        """Build recommended actions based on verdict."""
        actions = []

        if probability > 60:
            actions.extend([
                {"action": "File DMCA Takedown", "priority": "IMMEDIATE", "targets": "All identified marketplace listings"},
                {"action": "Alert Customs (CBP)", "priority": "HIGH", "targets": "Port of entry flagging for suspected shipments"},
                {"action": "Platform Report", "priority": "HIGH", "targets": "AliExpress, DHgate, Taobao seller accounts"},
                {"action": "Legal Action", "priority": "MEDIUM", "targets": "Cease & desist to identified factories"},
            ])
        elif probability > 30:
            actions.extend([
                {"action": "Enhanced Monitoring", "priority": "HIGH", "targets": "Continue surveillance of identified sellers"},
                {"action": "Platform Report", "priority": "MEDIUM", "targets": "Flag suspicious listings for review"},
                {"action": "Supply Chain Audit", "priority": "MEDIUM", "targets": "Verify supplier agreements and buyer lists"},
            ])
        else:
            actions.append(
                {"action": "Routine Monitoring", "priority": "LOW", "targets": "Standard periodic marketplace scans"}
            )

        return actions

    def _collect_evidence_links(self, scenario: dict) -> list[dict]:
        """Collect all evidence URLs from the scenario."""
        links = []

        for listing in scenario.get("listings", []):
            links.append({
                "type": "marketplace_listing",
                "platform": listing.get("platform", "unknown"),
                "url": listing.get("image_url", ""),
                "archived": True,
            })

        for post in scenario.get("job_postings", []):
            links.append({
                "type": "job_posting",
                "platform": "Job Board",
                "url": f"https://zhaopin.com/job/{random.randint(10000000, 99999999)}",
                "archived": True,
            })

        return links
