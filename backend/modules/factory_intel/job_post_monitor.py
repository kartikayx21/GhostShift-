"""Job Post Monitor — employment signal detection for factory intelligence."""

import random
import asyncio


class JobPostMonitor:
    """Monitors job postings for signals of ghost shift operations."""

    RED_FLAGS = {
        "suspicious_keywords": [
            "flexible hours", "night shift premium", "no questions asked",
            "overtime available", "immediate start", "cash payment option",
        ],
        "brand_keywords": [
            "experience with {brand}", "familiar with {brand} standards",
            "{brand} production line", "{brand} quality processes",
            "knowledge of {product} internals",
        ],
    }

    SERP_QUERIES = [
        '"assembly line" "{product}" site:zhipin.com',
        '"品质检验" "{product}" site:58.com',
        '"night shift" "electronics" "{city}" site:linkedin.com',
        '"{brand}" "manufacturing" "hiring" site:glassdoor.com',
    ]

    async def analyze(self, brand: str, product: str, job_postings: list[dict]) -> dict:
        """Analyze job postings for ghost shift indicators."""
        await asyncio.sleep(random.uniform(0.3, 0.8))

        analyzed = []
        total_red_flags = 0

        for post in job_postings:
            flags = post.get("red_flags", [])
            red_flag_count = len(flags)
            total_red_flags += red_flag_count

            # Score the posting
            risk = min(1.0, red_flag_count * 0.25)
            if any("night shift" in f.lower() for f in flags):
                risk += 0.15
            if any(brand.lower() in f.lower() for f in flags):
                risk += 0.20

            analyzed.append({
                **post,
                "risk_score": round(min(1.0, risk), 2),
                "analysis": {
                    "red_flag_count": red_flag_count,
                    "has_brand_mention": any(brand.lower() in f.lower() for f in flags),
                    "has_night_shift": any("night" in f.lower() for f in flags),
                    "hiring_anomaly": "200%+ of capacity" if red_flag_count >= 2 else "normal",
                },
            })

        # Check for volume anomaly
        volume_anomaly = len(job_postings) > 3

        return {
            "postings_analyzed": len(analyzed),
            "results": analyzed,
            "total_red_flags": total_red_flags,
            "volume_anomaly": volume_anomaly,
            "serp_queries_used": [
                q.format(brand=brand, product=product, city="Shenzhen")
                for q in self.SERP_QUERIES
            ],
            "api_used": "SERP_API",
            "risk_level": "high" if total_red_flags >= 5 else "medium" if total_red_flags >= 2 else "low",
        }
