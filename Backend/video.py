from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import cv2
from live_detection_utils import gen_live_detection

router = APIRouter()

def gen_raw_video():
    cap = cv2.VideoCapture(0)
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    finally:
        cap.release()

@router.get("/video_feed")
def video_feed():
    return StreamingResponse(gen_raw_video(), media_type='multipart/x-mixed-replace; boundary=frame')

@router.get("/live/ppe")
def live_ppe():
    return StreamingResponse(gen_live_detection('ppe'), media_type='multipart/x-mixed-replace; boundary=frame')

@router.get("/live/fire-smoke")
def live_fire_smoke():
    return StreamingResponse(gen_live_detection('fire-smoke'), media_type='multipart/x-mixed-replace; boundary=frame')

@router.get("/live/fall")
def live_fall():
    return StreamingResponse(gen_live_detection('fall'), media_type='multipart/x-mixed-replace; boundary=frame')
