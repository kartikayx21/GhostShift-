"""IP Fingerprint routes — product DNA extraction and comparison."""

from fastapi import APIRouter
from pydantic import BaseModel
from modules.ip_fingerprint import FingerprintScanner
from services.bright_data_router import router as bd_router

fingerprint_router = APIRouter(prefix="/api/fingerprint", tags=["IP Fingerprint"])
scanner = FingerprintScanner()


class FingerprintRequest(BaseModel):
    brand: str
    product: str
    custom_data: dict | None = None


class CompareRequest(BaseModel):
    brand: str
    product: str
    serials: list[str] | None = None


@fingerprint_router.post("/extract")
async def extract_fingerprint(req: FingerprintRequest):
    """Extract product DNA fingerprint from brand/product details."""
    fingerprint = scanner.extractor.extract(req.brand, req.product, req.custom_data)
    return {"status": "success", "fingerprint": fingerprint}


@fingerprint_router.post("/compare")
async def compare_fingerprint(req: CompareRequest):
    """Compare product fingerprint against marketplace listings."""
    # Get listings from BD router
    listing_data = await bd_router.execute("aliexpress_products", {
        "brand": req.brand,
        "product": req.product,
    })
    listings = listing_data.get("results", [])

    # Run full scan
    result = await scanner.scan(
        brand=req.brand,
        product=req.product,
        listings=listings,
        serials=req.serials,
    )
    return {"status": "success", **result}


@fingerprint_router.post("/validate-serial")
async def validate_serial(body: dict):
    """Validate a serial number against known patterns."""
    serial = body.get("serial", "")
    brand = body.get("brand", "")
    product = body.get("product", "")

    fingerprint = scanner.extractor.extract(brand, product)
    pattern = fingerprint.get("componentSignature", {}).get("serialPattern", {})
    result = scanner.serial_analyzer.validate_pattern(serial, pattern)

    return {"status": "success", "validation": result}
