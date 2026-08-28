# detector_registry.py - OOP Lifecycle & Detector Registry
from vision.ppe_detector import ppe_detector
from vision.fall_detector import fall_detector
from vision.fire_smoke_detector import fire_smoke_detector

class DetectorRegistry:
    def __init__(self):
        self.detectors = {
            "ppe": ppe_detector,
            "fall": fall_detector,
            "fire-smoke": fire_smoke_detector,
        }

    def get_detector(self, name: str):
        return self.detectors.get(name)

    def sleep(self, name: str):
        detector = self.detectors.get(name)
        if detector:
            detector.unload()

    def sleep_all(self):
        for detector in self.detectors.values():
            detector.unload()


detector_registry = DetectorRegistry()
