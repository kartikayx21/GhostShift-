import os
import asyncio
import random


class BrightDataClient:
    """Client for Bright Data web scraping APIs with mock mode fallback."""

    def __init__(self):
        self.api_key = os.environ.get("BRIGHTDATA_API_KEY", "")
        self.mock_mode = not bool(self.api_key.strip())

    async def search_marketplaces(self, brand: str, product: str) -> list[dict]:
        """Search marketplace platforms for suspicious listings."""
        if self.mock_mode:
            await asyncio.sleep(random.uniform(1.5, 3.0))
            retail_price = random.uniform(199.99, 999.99)
            return [
                {
                    "title": f"{brand} {product} Original Quality - Factory Direct",
                    "price": round(retail_price * 0.35, 2),
                    "retail_price": round(retail_price, 2),
                    "url": f"https://aliexpress.com/item/{random.randint(1000000, 9999999)}.html",
                    "platform": "AliExpress",
                    "seller_name": "ShenZhen TopTech Store",
                    "seller_rating": 4.2,
                    "monthly_sales": random.randint(500, 3000),
                    "image_url": f"https://placeholder.pics/svg/300/DEDEDE/555555/{brand}%20{product}",
                    "is_suspicious": True,
                },
                {
                    "title": f"Genuine {brand} {product} Wholesale Lot x50",
                    "price": round(retail_price * 0.28, 2),
                    "retail_price": round(retail_price, 2),
                    "url": f"https://dhgate.com/product/{random.randint(100000, 999999)}.html",
                    "platform": "DHgate",
                    "seller_name": "GuangzhouElectronicsCo",
                    "seller_rating": 3.8,
                    "monthly_sales": random.randint(200, 1500),
                    "image_url": f"https://placeholder.pics/svg/300/DEDEDE/555555/{brand}%20Wholesale",
                    "is_suspicious": True,
                },
                {
                    "title": f"{brand} {product} 1:1 Premium Copy AAA+",
                    "price": round(retail_price * 0.22, 2),
                    "retail_price": round(retail_price, 2),
                    "url": f"https://taobao.com/item/{random.randint(10000000, 99999999)}.html",
                    "platform": "Taobao",
                    "seller_name": "华强北数码旗舰店",
                    "seller_rating": 4.5,
                    "monthly_sales": random.randint(1000, 5000),
                    "image_url": f"https://placeholder.pics/svg/300/DEDEDE/555555/{brand}%20Copy",
                    "is_suspicious": True,
                },
                {
                    "title": f"Compatible Case for {brand} {product}",
                    "price": round(retail_price * 0.08, 2),
                    "retail_price": round(retail_price * 0.1, 2),
                    "url": f"https://aliexpress.com/item/{random.randint(1000000, 9999999)}.html",
                    "platform": "AliExpress",
                    "seller_name": "PhoneAccessoryWorld",
                    "seller_rating": 4.7,
                    "monthly_sales": random.randint(50, 300),
                    "image_url": f"https://placeholder.pics/svg/300/DEDEDE/555555/Case",
                    "is_suspicious": False,
                },
                {
                    "title": f"New {brand} {product} Unlocked - Best Price",
                    "price": round(retail_price * 0.45, 2),
                    "retail_price": round(retail_price, 2),
                    "url": f"https://dhgate.com/product/{random.randint(100000, 999999)}.html",
                    "platform": "DHgate",
                    "seller_name": "ShenzhenMobileHub",
                    "seller_rating": 3.5,
                    "monthly_sales": random.randint(800, 4000),
                    "image_url": f"https://placeholder.pics/svg/300/DEDEDE/555555/{brand}%20Unlocked",
                    "is_suspicious": True,
                },
            ]

        # Real mode — Bright Data Web Scraper API
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.brightdata.com/datasets/v3/trigger",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "dataset_id": "marketplace_search",
                    "query": f"{brand} {product}",
                    "platforms": ["aliexpress", "dhgate", "taobao"],
                },
                timeout=60.0,
            )
            response.raise_for_status()
            return response.json().get("results", [])

    async def search_suppliers(
        self, brand: str, product: str, components: list[str]
    ) -> list[dict]:
        """Search for component suppliers and trace supply chain."""
        if self.mock_mode:
            await asyncio.sleep(random.uniform(1.5, 3.0))
            return [
                {
                    "supplier_name": "Shenzhen HuaQiang Electronics Co., Ltd.",
                    "location": "Shenzhen, Guangdong, China",
                    "components_supplied": [components[0], components[2]] if len(components) > 2 else components[:1],
                    "known_buyers": [
                        {"name": brand, "suspicious": False},
                        {"name": "YuXin Technology Ltd.", "suspicious": True},
                        {"name": "JinHao Manufacturing Co.", "suspicious": True},
                    ],
                    "source_url": "https://1688.com/supplier/huaqiang-electronics",
                },
                {
                    "supplier_name": "Dongguan BatteryTech Power Systems",
                    "location": "Dongguan, Guangdong, China",
                    "components_supplied": [components[1]] if len(components) > 1 else components[:1],
                    "known_buyers": [
                        {"name": brand, "suspicious": False},
                        {"name": "NoName Tech Shenzhen", "suspicious": True},
                    ],
                    "source_url": "https://alibaba.com/supplier/batterytech-power",
                },
                {
                    "supplier_name": "Suzhou PrecisionMold Industrial",
                    "location": "Suzhou, Jiangsu, China",
                    "components_supplied": [components[3]] if len(components) > 3 else components[:1],
                    "known_buyers": [
                        {"name": brand, "suspicious": False},
                        {"name": f"{brand} (Subcontractor B)", "suspicious": False},
                    ],
                    "source_url": "https://1688.com/supplier/suzhou-precisionmold",
                },
                {
                    "supplier_name": "Zhongshan ChipDesign Semiconductor",
                    "location": "Zhongshan, Guangdong, China",
                    "components_supplied": [components[2]] if len(components) > 2 else components[:1],
                    "known_buyers": [
                        {"name": brand, "suspicious": False},
                        {"name": "GhostLine Electronics", "suspicious": True},
                        {"name": "ShadowTech Manufacturing", "suspicious": True},
                    ],
                    "source_url": "https://alibaba.com/supplier/zhongshan-chipdesign",
                },
            ]

        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.brightdata.com/datasets/v3/trigger",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "dataset_id": "supplier_search",
                    "query": f"{brand} {product} components",
                    "components": components,
                },
                timeout=60.0,
            )
            response.raise_for_status()
            return response.json().get("results", [])

    async def search_job_postings(self, brand: str, product: str) -> list[dict]:
        """Search for suspicious job postings in manufacturing regions."""
        if self.mock_mode:
            await asyncio.sleep(random.uniform(1.5, 3.0))
            job_postings = [
                {
                    "title": f"Senior {product} Assembly Line Supervisor",
                    "company": "YuXin Technology Ltd.",
                    "location": "Shenzhen, China",
                    "description": f"Experience with {brand} {product} production line required. Must understand {brand} QC processes and assembly procedures. Night shift availability preferred.",
                    "posted_date": "2026-05-15",
                    "suspicious_keywords": [
                        f"{brand} production line",
                        "night shift",
                        "QC processes",
                    ],
                    "source_url": "https://zhaopin.com/job/78234561",
                },
                {
                    "title": f"Quality Control Engineer - Consumer Electronics",
                    "company": "JinHao Manufacturing Co.",
                    "location": "Guangzhou, China",
                    "description": f"Seeking QC engineer familiar with {brand} quality standards. Knowledge of {product} internals and testing procedures. Competitive salary + housing allowance.",
                    "posted_date": "2026-05-10",
                    "suspicious_keywords": [
                        f"{brand} quality standards",
                        f"{product} internals",
                    ],
                    "source_url": "https://51job.com/job/45678923",
                },
                {
                    "title": f"Mold Design Engineer - Mobile Device Components",
                    "company": "GhostLine Electronics",
                    "location": "Shenzhen, China",
                    "description": f"Must have experience designing molds for premium smartphone casings. Prior {brand} factory experience is a strong plus. Reverse engineering capabilities valued.",
                    "posted_date": "2026-05-20",
                    "suspicious_keywords": [
                        f"{brand} factory experience",
                        "reverse engineering",
                        "premium smartphone casings",
                    ],
                    "source_url": "https://liepin.com/job/34567812",
                },
                {
                    "title": f"Supply Chain Manager - Electronics Manufacturing",
                    "company": "ShadowTech Manufacturing",
                    "location": "Guangzhou, China",
                    "description": f"Managing component procurement for consumer electronics. Must have existing relationships with {brand} tier-1 suppliers. Discretion required.",
                    "posted_date": "2026-05-18",
                    "suspicious_keywords": [
                        f"{brand} tier-1 suppliers",
                        "discretion required",
                    ],
                    "source_url": "https://zhaopin.com/job/89012345",
                },
            ]

            employee_movements = [
                {
                    "name": "Zhang Wei",
                    "previous_employer": f"{brand} Manufacturing (Shenzhen)",
                    "current_employer": "YuXin Technology Ltd.",
                    "role": "Production Line Director",
                    "linkedin_url": "https://linkedin.com/in/zhangwei-production",
                },
                {
                    "name": "Li Xiaoming",
                    "previous_employer": f"{brand} Quality Assurance",
                    "current_employer": "GhostLine Electronics",
                    "role": "Chief Quality Officer",
                    "linkedin_url": "https://linkedin.com/in/lixiaoming-qa",
                },
                {
                    "name": "Wang Fang",
                    "previous_employer": f"{brand} Supply Chain Division",
                    "current_employer": "ShadowTech Manufacturing",
                    "role": "VP of Procurement",
                    "linkedin_url": "https://linkedin.com/in/wangfang-supply",
                },
            ]

            return {
                "job_postings": job_postings,
                "employee_movements": employee_movements,
            }

        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.brightdata.com/datasets/v3/trigger",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "dataset_id": "job_postings",
                    "query": f"{brand} {product} manufacturing",
                    "locations": ["Shenzhen", "Guangzhou", "Dongguan"],
                },
                timeout=60.0,
            )
            response.raise_for_status()
            return response.json()

    async def get_product_images(self, brand: str, product: str) -> list[dict]:
        """Get product images from marketplace listings for forensic analysis."""
        if self.mock_mode:
            await asyncio.sleep(random.uniform(1.5, 3.0))
            return [
                {
                    "url": f"https://placeholder.pics/svg/600/DEDEDE/555555/{brand}%20{product}%20Front",
                    "source_platform": "AliExpress",
                    "listing_title": f"{brand} {product} Original Quality - Front View",
                },
                {
                    "url": f"https://placeholder.pics/svg/600/DEDEDE/555555/{brand}%20{product}%20Back",
                    "source_platform": "DHgate",
                    "listing_title": f"Genuine {brand} {product} - Back Panel Detail",
                },
                {
                    "url": f"https://placeholder.pics/svg/600/DEDEDE/555555/{brand}%20{product}%20Box",
                    "source_platform": "Taobao",
                    "listing_title": f"{brand} {product} Full Kit with Packaging",
                },
            ]

        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.brightdata.com/datasets/v3/trigger",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "dataset_id": "product_images",
                    "query": f"{brand} {product}",
                },
                timeout=60.0,
            )
            response.raise_for_status()
            return response.json().get("images", [])


# Singleton instance
brightdata = BrightDataClient()
