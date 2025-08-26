from fastapi import APIRouter, UploadFile
from fastapi.responses import JSONResponse
import numpy as np
import cv2
import os
from ultralytics import YOLO
from ppe_model import detect_ppe, ppe_model, CLASS_NAMES
from fire_smoke_model import detect_fire_smoke, fire_model, FIRE_CLASSES
from restricted_area_model import detect_restricted_area, restricted_model
from fall_model import detect_fall, fall_model

router = APIRouter()

class ModelRegistry:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.models = {}
        self.model_paths = {}
        self.errors = {}
        self._load_models()

    def _load_models(self):
        for root, _, files in os.walk(self.base_dir):
            for f in files:
                if f.endswith('.pt'):
                    pt_path = os.path.join(root, f)
                    model_name = self._model_name_from_path(pt_path)
                    try:
                        self.models[model_name] = YOLO(pt_path)
                        self.model_paths[model_name] = pt_path
                    except Exception as e:
                        self.models[model_name] = None
                        self.model_paths[model_name] = pt_path
                        self.errors[model_name] = str(e)

    def _model_name_from_path(self, path):
        rel = os.path.relpath(path, self.base_dir)
        name = rel.replace('\\', '/').replace('/', '__').replace('.pt', '')
        return name

    def get(self, model_name):
        return self.models.get(model_name)

    def list_models(self):
        return list(self.models.keys())

    def get_error(self, model_name):
        return self.errors.get(model_name)

    def get_path(self, model_name):
        return self.model_paths.get(model_name)

model_registry = ModelRegistry(os.path.join(os.path.dirname(__file__), '../Models'))
print("Loaded models:", model_registry.list_models())

@router.post("/detect/model/{model_name}")
def detect_with_model(model_name: str, file: UploadFile):
    model = model_registry.get(model_name)
    if model is None:
        err = model_registry.get_error(model_name)
        if err:
            return JSONResponse({"error": f"Model failed to load: {err}"}, status_code=500)
        return JSONResponse({"error": "Model not found."}, status_code=404)
    contents = file.file.read()
    npimg = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    try:
        results = model(img)
    except Exception as e:
        return JSONResponse({"error": f"Model inference failed: {e}"}, status_code=500)
    detections = []
    for r in results:
        if hasattr(r, 'boxes'):
            for box in r.boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                conf = float(box.conf[0])
                cls = int(box.cls[0]) if hasattr(box, 'cls') else -1
                detections.append({
                    "bbox": [int(x1), int(y1), int(x2), int(y2)],
                    "confidence": conf,
                    "label": str(cls)
                })
        if hasattr(r, 'keypoints'):
            for kp in r.keypoints.xy:
                detections.append({"keypoints": kp.tolist()})
    return {"detections": detections}

@router.post("/detect/ppe/")
def detect_ppe_api(file: UploadFile):
    if not ppe_model:
        return JSONResponse({"error": "PPE model not loaded."}, status_code=500)
    contents = file.file.read()
    npimg = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    detections = detect_ppe(img)
    return {"detections": detections}

@router.post("/detect/fire-smoke/")
def detect_fire_smoke_api(file: UploadFile):
    if not fire_model:
        return JSONResponse({"error": "Fire/Smoke model not loaded."}, status_code=500)
    contents = file.file.read()
    npimg = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    detections = detect_fire_smoke(img)
    return {"detections": detections}

@router.post("/detect/restricted-area/")
def detect_restricted_area_api(file: UploadFile):
    if not restricted_model:
        return JSONResponse({"error": "Restricted Area model not loaded."}, status_code=500)
    contents = file.file.read()
    npimg = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    detections = detect_restricted_area(img)
    return {"detections": detections}

@router.post("/detect/fall/")
def detect_fall_api(file: UploadFile):
    if not fall_model:
        return JSONResponse({"error": "Fall model not loaded."}, status_code=500)
    contents = file.file.read()
    npimg = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    detections = detect_fall(img)
    return {"detections": detections}
