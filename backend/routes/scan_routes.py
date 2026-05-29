"""Marketplace scan routes — POST /api/scan/* endpoints."""

import asyncio
from fastapi import APIRouter
from pydantic import BaseModel
from services.bright_data_router import router as bd_router

scan_router = APIRouter(prefix="/api/scan", tags=["Marketplace Scan"])


class ScanRequest(BaseModel):
    brand: str
    product: str
    price_max: float | None = None


@scan_router.post("/aliexpress")
async def scan_aliexpress(req: ScanRequest):
    """Scan AliExpress for suspicious listings via Bright Data Web Scraper API."""
    result = await bd_router.execute("aliexpress_products", {
        "brand": req.brand,
        "product": req.product,
        "price_max": req.price_max,
    })
    return {
        "platform": "AliExpress",
        "dataset_id": bd_router.get_dataset_id("aliexpress"),
        "api": "WEB_SCRAPER",
        **result,
    }


@scan_router.post("/dhgate")
async def scan_dhgate(req: ScanRequest):
    """Scan DHgate for suspicious listings via Bright Data Web Scraper API."""
    result = await bd_router.execute("dhgate_listings", {
        "brand": req.brand,
        "product": req.product,
        "price_max": req.price_max,
    })
    return {
        "platform": "DHgate",
        "dataset_id": bd_router.get_dataset_id("dhgate"),
        "api": "WEB_SCRAPER",
        **result,
    }


@scan_router.post("/taobao")
async def scan_taobao(req: ScanRequest):
    """Scan Taobao for suspicious listings via Bright Data Web Scraper API (proxy)."""
    result = await bd_router.execute("taobao_listings", {
        "brand": req.brand,
        "product": req.product,
        "price_max": req.price_max,
    })
    return {
        "platform": "Taobao",
        "dataset_id": bd_router.get_dataset_id("taobao"),
        "api": "WEB_SCRAPER",
        **result,
    }
