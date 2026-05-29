"""Supply chain routes — graph data and suspicious path API."""

from fastapi import APIRouter
from pydantic import BaseModel
from modules.supply_chain import SupplyChainGraph
from services.bright_data_router import router as bd_router

supply_chain_router = APIRouter(prefix="/api/supply-chain", tags=["Supply Chain"])


class SupplyChainRequest(BaseModel):
    brand: str
    product: str
    scenario: str | None = None


@supply_chain_router.post("/graph")
async def get_supply_chain_graph(req: SupplyChainRequest):
    """Get supply chain graph data (nodes + edges)."""
    scenario_name = req.scenario or "ghost_shift"

    # Pick scenario based on brand
    if "dyson" in req.brand.lower():
        scenario_name = "clean_supplier"
    elif "samsung" in req.brand.lower():
        scenario_name = "copycat_supplier"

    scenario = bd_router.get_scenario(scenario_name)
    graph = SupplyChainGraph()
    graph.build_from_scenario(scenario)

    return {
        "status": "success",
        "scenario": scenario_name,
        "graph": graph.get_graph_data(),
    }


@supply_chain_router.post("/suspicious-paths")
async def get_suspicious_paths(req: SupplyChainRequest):
    """Get highlighted suspicious paths in the supply chain."""
    scenario_name = req.scenario or "ghost_shift"
    if "dyson" in req.brand.lower():
        scenario_name = "clean_supplier"
    elif "samsung" in req.brand.lower():
        scenario_name = "copycat_supplier"

    scenario = bd_router.get_scenario(scenario_name)
    graph = SupplyChainGraph()
    graph.build_from_scenario(scenario)
    paths = graph.find_suspicious_paths()

    return {
        "status": "success",
        "paths": paths,
        "total_paths": len(paths),
        "high_risk_paths": sum(1 for p in paths if p.get("risk") == "high"),
    }
