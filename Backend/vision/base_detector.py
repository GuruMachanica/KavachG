# base_detector.py - Abstract Base Vision Detector Class
from abc import ABC, abstractmethod
import os
import torch
from ultralytics import YOLO

class BaseVisionDetector(ABC):
    def __init__(self, model_path: str, task: str = None):
        self.model_path = model_path
        self.task = task
        self._model = None
        self._device = "cuda" if torch.cuda.is_available() else "cpu"

    @property
    def model(self):
        if self._model is None and os.path.exists(self.model_path):
            self._model = YOLO(self.model_path, task=self.task) if self.task else YOLO(self.model_path)
        return self._model

    def unload(self):
        self._model = None

    @abstractmethod
    def detect(self, img, conf_threshold: float = 0.25) -> list:
        pass
