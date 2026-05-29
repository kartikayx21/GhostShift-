"""Forensics routes — listing forensics, dossier, and probability API."""

import asyncio
from fastapi import APIRouter
from pydantic import BaseModel
from modules.listing_forensics import ImageAnalyzer, SerialValidator, PriceThresholdModel
from modules.ghost_shift import GhostShiftModel, EvidenceDossierGenerator, AlertSystem
from modules.factory_intel import JobPostMonitor, EmployeeTracker, KnowledgeTransferDetector
from services.bright_data_router import router as bd_router

forensics_router = APIRouter(prefix="/api/forensics", tags=["Forensics"])

image_analyzer = ImageAnalyzer()
serial_validator = SerialValidator()
price_model = PriceThresholdModel()
ghost_model = GhostShiftModel()
dossier_gen = EvidenceDossierGenerator()
alert_system = AlertSystem()
job_monitor = JobPostMonitor()
employee_tracker = EmployeeTracker()
kt_detector = KnowledgeTransferDetector()


class ForensicsRequest(BaseModel):
    brand: str
    product: str
    scenario: str | None = None


class SerialRequest(BaseModel):
    serial: str
    brand: str
    product: str


class PricingRequest(BaseModel):
    listing_price: float
    genuine_price: float
    product_category: str = "default"
    shipping_route: str = "CN→US"


@forensics_router.post("/full-analysis")
async def full_forensic_analysis(req: ForensicsRequest):
    """Run complete forensic analysis pipeline — all modules in parallel."""
    scenario_name = req.scenario or "ghost_shift"
    if "dyson" in req.brand.lower():
        scenario_name = "clean_supplier"
    elif "samsung" in req.brand.lower():
        scenario_name = "copycat_supplier"

    scenario = bd_router.get_scenario(scenario_name)

    # Run all analyses in parallel
    image_task = image_analyzer.analyze(req.brand, req.product, scenario)
    job_task = job_monitor.analyze(req.brand, req.product, scenario.get("job_postings", []))
    employee_task = employee_tracker.analyze(req.brand, req.product, scenario.get("employee_movements", []))

    image_result, job_result, employee_result = await asyncio.gather(
        image_task, job_task, employee_task
    )

    # Knowledge transfer
    kt_result = await kt_detector.analyze(employee_result, scenario.get("factory", {}))

    # Pricing
    pricing = scenario.get("pricing_analysis", {})
    price_result = price_model.analyze(
        pricing.get("average_listing_price", 0),
        pricing.get("genuine_price", 0),
    )

    # Ghost shift probability
    probability_result = ghost_model.calculate_from_scenario(scenario)

    # Alert
    alert = alert_system.evaluate(
        probability_result["probability"],
        scenario_name, req.brand, req.product,
    )

    # Dossier
    dossier = await dossier_gen.generate(scenario, probability_result)

    return {
        "status": "success",
        "scenario": scenario_name,
        "probability": probability_result,
        "alert": alert,
        "image_forensics": image_result,
        "job_intelligence": job_result,
        "employee_intelligence": employee_result,
        "knowledge_transfer": kt_result,
        "pricing_analysis": price_result,
        "dossier": dossier,
    }


@forensics_router.post("/analyze-serial")
async def analyze_serial(req: SerialRequest):
    """Validate a serial number against known patterns."""
    scenario = bd_router.get_scenario("ghost_shift")
    result = serial_validator.validate(req.serial, scenario)
    return {"status": "success", "validation": result}


@forensics_router.post("/analyze-pricing")
async def analyze_pricing(req: PricingRequest):
    """Run pricing threshold analysis."""
    result = price_model.analyze(
        req.listing_price,
        req.genuine_price,
        product_category=req.product_category,
        shipping_route=req.shipping_route,
    )
    return {"status": "success", "analysis": result}


@forensics_router.post("/probability")
async def calculate_probability(req: ForensicsRequest):
    """Calculate ghost shift probability from scenario data."""
    scenario_name = req.scenario or "ghost_shift"
    if "dyson" in req.brand.lower():
        scenario_name = "clean_supplier"
    elif "samsung" in req.brand.lower():
        scenario_name = "copycat_supplier"

    scenario = bd_router.get_scenario(scenario_name)
    result = ghost_model.calculate_from_scenario(scenario)
    alert = alert_system.evaluate(result["probability"], scenario_name, req.brand, req.product)

    return {"status": "success", "probability": result, "alert": alert}


@forensics_router.post("/dossier")
async def generate_dossier(req: ForensicsRequest):
    """Generate evidence dossier for a scenario."""
    scenario_name = req.scenario or "ghost_shift"
    if "dyson" in req.brand.lower():
        scenario_name = "clean_supplier"
    elif "samsung" in req.brand.lower():
        scenario_name = "copycat_supplier"

    scenario = bd_router.get_scenario(scenario_name)
    probability = ghost_model.calculate_from_scenario(scenario)
    dossier = await dossier_gen.generate(scenario, probability)

    return {"status": "success", "dossier": dossier, "probability": probability}
