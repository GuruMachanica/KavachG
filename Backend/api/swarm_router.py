# swarm_router.py - Multi-Agent Autonomous Safety Swarm API Endpoints
from fastapi import APIRouter, Body, Depends
from auth import get_current_user
from autonomous_swarm import swarm_engine

router = APIRouter()


@router.get("/swarm/status")
def get_swarm_status(user: dict = Depends(get_current_user)):
    return swarm_engine.get_status()


@router.post("/swarm/patrol/toggle")
def toggle_swarm_patrol(payload: dict = Body(default={}), user: dict = Depends(get_current_user)):
    active = payload.get("active")
    new_state = swarm_engine.toggle_patrol(active)
    return {
        "message": f"Autonomous Patrol Swarm {'activated' if new_state else 'paused'}",
        "patrol_active": new_state
    }
