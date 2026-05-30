"""Bright Data routing layer — decides which BD product handles each scraping task."""

import os
import json
import asyncio
import random
from pathlib import Path


# Load mock scenarios at module level
MOCK_SCENARIOS_DIR = Path(__file__).parent.parent / "data" / "mock_scenarios"


def _load_scenario(name: str) -> dict:
    fpath = MOCK_SCENARIOS_DIR / name
    if fpath.exists():
        with open(fpath, encoding="utf-8") as f:
            return json.load(f)
    return {}


MOCK_SCENARIOS = {
    "ghost_shift": _load_scenario("ghost_shift_demo.json"),
    "copycat_supplier": _load_scenario("copycat_supplier_demo.json"),
    "clean_supplier": _load_scenario("clean_supplier_demo.json"),
}


class BrightDataRouter:
    """Master routing layer that decides which Bright Data product handles each task."""

    # Real Bright Data dataset IDs
    SCRAPER_DATASETS = {
        "aliexpress": "gd_l7q7dkf244hwjntr0",
        "dhgate": "gd_ltr9h79j1m20p9td5n",
        "taobao": "gd_l1vikfch901nx3by4o",
        "amazon_products": "gd_l7q7dkf244hwjntr0",
        "walmart": "gd_l7q7dkf244hwjntr0",
    }

    ROUTING_TABLE = {
        # Web Scraper API — structured, fast, dataset-based
        "aliexpress_products": {"api": "WEB_SCRAPER", "dataset": "aliexpress"},
        "dhgate_listings": {"api": "WEB_SCRAPER", "dataset": "dhgate"},
        "taobao_listings": {"api": "WEB_SCRAPER", "dataset": "taobao"},
        "amazon_asins": {"api": "WEB_SCRAPER", "dataset": "amazon_products"},
        "walmart_products": {"api": "WEB_SCRAPER", "dataset": "walmart"},
        # Web Unlocker — geo-restricted, auth-walled, simple pages
        "panjiva_records": {"api": "WEB_UNLOCKER", "note": "trade records, needs US IP"},
        "supplier_directories": {"api": "WEB_UNLOCKER", "note": "Made-in-China, Global Sources"},
        "importyeti_data": {"api": "WEB_UNLOCKER"},
        "canton_fair_attendees": {"api": "WEB_UNLOCKER"},
        # Scraping Browser — heavy JS, anti-bot, dynamic content
        "alibaba_storefront": {"api": "SCRAPING_BROWSER", "note": "Heavy JS, requires browser"},
        "linkedin_profiles": {"api": "SCRAPING_BROWSER", "note": "Requires session simulation"},
        "glassdoor_reviews": {"api": "SCRAPING_BROWSER"},
        "made_in_china_b2b": {"api": "SCRAPING_BROWSER"},
        "1688_cn_wholesale": {"api": "SCRAPING_BROWSER", "note": "Chinese domestic, geo-required"},
        # SERP API — news, legal records, indexed content
        "ip_lawsuit_news": {"api": "SERP_API", "query_template": 'site:justia.com OR site:courtlistener.com "{brand}"'},
        "customs_seizure_news": {"api": "SERP_API", "query_template": 'counterfeit seizure "{brand}" "{product}"'},
        "job_post_intel": {"api": "SERP_API", "query_template": 'site:zhipin.com OR site:linkedin.com "{product}" assembly'},
        "factory_news": {"api": "SERP_API"},
    }

    UNLOCKER_TARGETS = [
        "https://www.importyeti.com/company/{supplier_name}",
        "https://panjiva.com/search?q={chip_id}",
        "https://volza.com/p/{hs_code}/import/",
    ]

    def __init__(self):
        self.api_key = os.environ.get("BRIGHTDATA_API_KEY", "")
        self.mock_mode = not bool(self.api_key.strip())

    def route(self, task: str) -> dict:
        """Get the routing info for a given task."""
        return self.ROUTING_TABLE.get(task, {"api": "WEB_UNLOCKER", "note": "default fallback"})

    def get_dataset_id(self, platform: str) -> str:
        """Get the real Bright Data dataset ID for a platform."""
        return self.SCRAPER_DATASETS.get(platform, "")

    async def execute(self, task: str, params: dict) -> dict:
        """Execute a scraping task — real or mock."""
        if self.mock_mode:
            return await self.get_mock_data(task, params)

        routing = self.route(task)
        api = routing["api"]

        if api == "WEB_SCRAPER":
            return await self._execute_web_scraper(task, params, routing)
        elif api == "WEB_UNLOCKER":
            return await self._execute_web_unlocker(task, params, routing)
        elif api == "SCRAPING_BROWSER":
            return await self._execute_scraping_browser(task, params, routing)
        elif api == "SERP_API":
            return await self._execute_serp_api(task, params, routing)
        else:
            return await self.get_mock_data(task, params)

    async def _execute_web_scraper(self, task: str, params: dict, routing: dict) -> dict:
        """Execute via Bright Data Web Scraper API."""
        import httpx

        dataset_id = self.SCRAPER_DATASETS.get(routing.get("dataset", ""), "")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.brightdata.com/datasets/v3/trigger",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "dataset_id": dataset_id,
                        "keyword": f"{params.get('brand', '')} {params.get('product', '')}",
                        "price_max": params.get("price_max"),
                        "fields": params.get("fields", ["title", "price", "seller_id", "images"]),
                    },
                    timeout=60.0,
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"[WARN] Web Scraper API failed for {task}: {e} — falling back to mock")
            return await self.get_mock_data(task, params)

    async def _execute_web_unlocker(self, task: str, params: dict, routing: dict) -> dict:
        """Execute via Bright Data Web Unlocker (proxy)."""
        # Real implementation would route through BD proxy
        # For now, fall back to mock
        return await self.get_mock_data(task, params)

    async def _execute_scraping_browser(self, task: str, params: dict, routing: dict) -> dict:
        """Execute via Bright Data Scraping Browser (Playwright/CDP)."""
        # Real implementation would use Playwright + BD browser endpoint
        return await self.get_mock_data(task, params)

    async def _execute_serp_api(self, task: str, params: dict, routing: dict) -> dict:
        """Execute via Bright Data SERP API."""
        import httpx

        query_template = routing.get("query_template", "{brand} {product}")
        query = query_template.format(**params)
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.brightdata.com/serp/req",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={"query": query, "country": "us"},
                    timeout=60.0,
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"[WARN] SERP API failed for {task}: {e} — falling back to mock")
            return await self.get_mock_data(task, params)

    async def get_mock_data(self, task: str, params: dict) -> dict:
        """Return realistic mock data for a task."""
        await asyncio.sleep(random.uniform(0.5, 1.5))

        brand = params.get("brand", "").lower()
        product = params.get("product", "").lower()

        # Pick best scenario based on brand/product
        if "dyson" in brand:
            scenario = MOCK_SCENARIOS.get("clean_supplier", {})
        elif "samsung" in brand or "galaxy" in product:
            scenario = MOCK_SCENARIOS.get("copycat_supplier", {})
        else:
            scenario = MOCK_SCENARIOS.get("ghost_shift", {})

        # Return task-specific data from the scenario
        task_mapping = {
            "aliexpress_products": scenario.get("listings", []),
            "dhgate_listings": scenario.get("listings", []),
            "taobao_listings": scenario.get("listings", []),
            "panjiva_records": scenario.get("component_overlap", {}),
            "supplier_directories": scenario.get("supply_chain_graph", {}),
            "job_post_intel": scenario.get("job_postings", []),
            "linkedin_profiles": scenario.get("employee_movements", []),
            "customs_seizure_news": [],
            "ip_lawsuit_news": [],
        }

        return {"task": task, "api": self.route(task)["api"], "results": task_mapping.get(task, scenario)}

    def get_scenario(self, scenario_name: str) -> dict:
        """Get a full pre-built scenario by name."""
        return MOCK_SCENARIOS.get(scenario_name, MOCK_SCENARIOS.get("ghost_shift", {}))


# Singleton
router = BrightDataRouter()
