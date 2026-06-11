import os
import asyncio
from fastapi import FastAPI, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, Any

from app.models import TaskState
from app.agents.master import MasterAgent
from app import config

app = FastAPI(
    title="AEGIS Control API",
    description="Autonomous Crisis Intelligence System Multi-Agent API",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global system state
current_state = TaskState()

# Track active background tasks
active_tasks = {}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "frontend"))

@app.get("/api/state")
async def get_state():
    """Return the current system task state."""
    return current_state

@app.get("/api/config")
async def get_config():
    """Return the current system limits and severity configurations."""
    return {
        "MAX_BUDGET": config.MAX_BUDGET,
        "MAX_RISK": config.MAX_RISK,
        "MIN_COVERAGE": config.MIN_COVERAGE,
        "SEVERITY_LABELS": config.SEVERITY_LABELS
    }

@app.post("/api/reset")
async def reset_state():
    """Reset the current system task state and cancel active runs."""
    global current_state
    
    # Cancel active background tasks
    for task_name, task in active_tasks.items():
        if not task.done():
            task.cancel()
    active_tasks.clear()
    
    current_state = TaskState()
    return {"status": "reset", "state": current_state}

@app.post("/api/run_full")
async def run_full(payload: Optional[Dict[str, str]] = Body(default=None)):
    """
    Starts the full AEGIS orchestration flow in the background as an async task.
    Supports preset variants ('variant_a', 'variant_b', 'variant_c') and modes ('auto', 'step').
    """
    global current_state
    
    # Cancel any active tasks first
    for task_name, task in list(active_tasks.items()):
        if not task.done():
            task.cancel()
            
    # Initialize fresh state
    current_state = TaskState()
    
    variant = payload.get("variant", "variant_a") if payload else "variant_a"
    mode = payload.get("mode", "auto") if payload else "auto"
    
    current_state.execution_mode = mode
    current_state.status = "running"
    
    master = MasterAgent()
    # Schedule master orchestration task asynchronously in background
    task = asyncio.create_task(master.run_async(current_state, variant))
    active_tasks["orchestration"] = task
    
    return {"status": "started", "state": current_state}

@app.post("/api/pause")
async def pause():
    """Pause execution (Hold in loop)."""
    global current_state
    current_state.execution_mode = "paused"
    return {"status": "paused", "state": current_state}

@app.post("/api/resume")
async def resume():
    """Resume execution (Shift back to auto)."""
    global current_state
    current_state.execution_mode = "auto"
    current_state.status = "running"
    return {"status": "resumed", "state": current_state}

@app.post("/api/step")
async def step():
    """Run a single agent step and pause again."""
    global current_state
    
    # If not running yet, start the flow in step mode
    if current_state.status == "ready":
        await run_full({"variant": "variant_a", "mode": "step"})
        return {"status": "started_step", "state": current_state}
        
    current_state.execution_mode = "step"
    current_state.status = "running"
    return {"status": "stepping", "state": current_state}

@app.post("/api/stop")
async def stop():
    """Manually terminate execution."""
    global current_state
    current_state.status = "stopped"
    current_state.execution_mode = "paused"
    return {"status": "stopped", "state": current_state}

@app.post("/api/replan")
async def replan(payload: Dict[str, str] = Body(...)):
    """Inject disruption event and trigger replanning."""
    global current_state
    event_type = payload.get("event_type")
    if not event_type:
        raise HTTPException(status_code=400, detail="event_type parameter is required.")
        
    master = MasterAgent()
    # Replanning runs fully, schedule in background
    task = asyncio.create_task(master.run_replan_async(current_state, event_type))
    active_tasks["replanning"] = task
    
    return {"status": "replanning_started", "state": current_state}

# Serve frontend static files
if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
else:
    @app.get("/")
    def read_root():
        return {
            "message": "AEGIS APIs running. Frontend folder not detected at workspace root.",
            "frontend_resolved_path": FRONTEND_DIR
        }
