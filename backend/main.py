import os
import sys
import asyncio
import json

from dotenv import load_dotenv

# Load env vars BEFORE importing modules that read them at import time
load_dotenv()

# Ensure backend directory is on sys.path for imports
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

from models import InvestigationRequest
from services.database import db
from orchestrator import InvestigationOrchestrator, active_orchestrators
from routes.scan_routes import scan_router
from routes.fingerprint_routes import fingerprint_router
from routes.supply_chain_routes import supply_chain_router
from routes.forensics_routes import forensics_router

app = FastAPI(title="Ghost Shift API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register new module routers
app.include_router(scan_router)
app.include_router(fingerprint_router)
app.include_router(supply_chain_router)
app.include_router(forensics_router)


@app.post("/api/investigate")
async def start_investigation(req: InvestigationRequest):
    """Start a new ghost shift investigation for a brand/product."""
    investigation = db.create_investigation(req.brand, req.product)
    orchestrator = InvestigationOrchestrator(investigation.id)
    active_orchestrators[investigation.id] = orchestrator
    asyncio.create_task(orchestrator.run(req.brand, req.product))
    return {"investigation_id": investigation.id}


@app.get("/api/investigate/{investigation_id}/status")
async def get_status(investigation_id: str):
    """Get current investigation status and agent progress."""
    inv = db.get_investigation(investigation_id)
    if not inv:
        raise HTTPException(404, "Investigation not found")

    agents = []
    for key, agent_status in inv.agents.items():
        agents.append(
            {
                "name": agent_status.name,
                "status": agent_status.status.value,
                "findings_count": agent_status.findings_count,
            }
        )

    completed = sum(
        1 for a in inv.agents.values() if a.status.value in ("complete", "error")
    )
    running = sum(1 for a in inv.agents.values() if a.status.value == "running")
    progress = int((completed / len(inv.agents)) * 100)
    if running > 0 and progress < 100:
        progress = max(progress, int(((completed + 0.5) / len(inv.agents)) * 100))

    return {
        "status": inv.status,
        "brand": inv.brand,
        "product": inv.product,
        "agents": agents,
        "overall_progress": progress,
    }


@app.get("/api/investigate/{investigation_id}/results")
async def get_results(investigation_id: str):
    """Get final investigation results (only available after completion)."""
    inv = db.get_investigation(investigation_id)
    if not inv:
        raise HTTPException(404, "Investigation not found")
    if not inv.result:
        raise HTTPException(400, "Investigation not yet complete")

    return {
        "risk_score": inv.result.risk_score,
        "verdict": inv.result.verdict,
        "evidence": [e.model_dump() for e in inv.result.evidence],
        "recommended_action": inv.result.recommended_action,
        "brand": inv.brand,
        "product": inv.product,
    }


@app.get("/api/investigate/{investigation_id}/stream")
async def stream_events(investigation_id: str):
    """SSE stream for real-time investigation events."""
    inv = db.get_investigation(investigation_id)
    if not inv:
        raise HTTPException(404, "Investigation not found")

    orchestrator = active_orchestrators.get(investigation_id)

    async def event_generator():
        if not orchestrator:
            # Investigation already complete, send current state
            yield {
                "event": "status",
                "data": json.dumps({"status": inv.status}),
            }
            return

        while True:
            try:
                event = await asyncio.wait_for(
                    orchestrator.event_queue.get(), timeout=30.0
                )
                yield {
                    "event": event.get("event", "message"),
                    "data": json.dumps(event.get("data", {})),
                }
                if event.get("event") == "complete":
                    break
            except asyncio.TimeoutError:
                yield {"event": "ping", "data": "{}"}

    return EventSourceResponse(event_generator())


@app.get("/api/investigations")
async def list_investigations():
    """List all investigations, most recent first."""
    investigations = db.list_investigations()
    return [
        {
            "id": inv.id,
            "brand": inv.brand,
            "product": inv.product,
            "status": inv.status,
            "risk_score": inv.result.risk_score if inv.result else None,
            "created_at": inv.created_at,
        }
        for inv in investigations
    ]


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
