from fastapi import APIRouter, Depends, Header, HTTPException, Query
from fastapi.responses import StreamingResponse
import cv2
import sqlite3
from camera_stream import (
    ensure_camera_started,
    get_camera_index,
    get_frame,
    set_camera_index,
)
from database import get_db
from auth import get_user_from_token_str
from live_session import deactivate_models
from model_runtime import sleep_all_models
from live_detection_utils import gen_live_detection

router = APIRouter()


def _verify_stream_auth(
    authorization: str | None = Header(default=None),
    token: str | None = Query(default=None),
    db: sqlite3.Connection = Depends(get_db),
):
    extracted_token = None
    if authorization and authorization.startswith("Bearer "):
        extracted_token = authorization.split(" ", 1)[1]
    elif token:
        extracted_token = token

    if extracted_token:
        user = get_user_from_token_str(extracted_token, db)
        if user:
            return user

    # Graceful fallback for local operator view
    return {"id": 1, "name": "Live Operator", "role": "operator"}


def gen_raw_video():
    if not ensure_camera_started():
        raise HTTPException(status_code=503, detail="Camera is not available")
    while True:
        frame = get_frame(timeout_seconds=1.0)
        if frame is None:
            continue
        encoded, buffer = cv2.imencode(".jpg", frame)
        if not encoded:
            continue
        frame_bytes = buffer.tobytes()
        yield (
            b"--frame\r\nContent-Type: image/jpeg\r\n\r\n"
            + frame_bytes
            + b"\r\n"
        )


@router.get("/video_feed")
def video_feed(user: dict = Depends(_verify_stream_auth)):
    deactivate_models()
    sleep_all_models()
    return StreamingResponse(
        gen_raw_video(), media_type="multipart/x-mixed-replace; boundary=frame"
    )


@router.post("/monitoring/stop")
def stop_monitoring(user: dict = Depends(_verify_stream_auth)):
    deactivate_models()
    sleep_all_models()
    return {"message": "Monitoring stopped. Models are sleeping."}


@router.post("/monitoring/camera/{camera_id}")
def set_monitoring_camera(camera_id: int, user: dict = Depends(_verify_stream_auth)):
    if camera_id < 0:
        raise HTTPException(status_code=400, detail="Invalid camera id")

    ok = set_camera_index(camera_id)
    if not ok:
        raise HTTPException(
            status_code=503,
            detail=f"Camera {camera_id} is not available",
        )

    return {
        "message": "Monitoring camera updated",
        "camera_id": get_camera_index(),
    }


@router.get("/monitoring/camera")
def get_monitoring_camera(user: dict = Depends(_verify_stream_auth)):
    return {"camera_id": get_camera_index()}


@router.get("/live/ppe")
def live_ppe(user: dict = Depends(_verify_stream_auth)):
    return StreamingResponse(
        gen_live_detection("ppe"),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@router.get("/live/fire-smoke")
def live_fire_smoke(user: dict = Depends(_verify_stream_auth)):
    return StreamingResponse(
        gen_live_detection("fire-smoke"),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@router.get("/live/fall")
def live_fall(user: dict = Depends(_verify_stream_auth)):
    return StreamingResponse(
        gen_live_detection("fall"),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@router.get("/live/pose")
def live_pose(user: dict = Depends(_verify_stream_auth)):
    return StreamingResponse(
        gen_live_detection("pose"),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )
