from datetime import datetime
from db_handler import SafetyDB, Incident, IncidentType, Severity
import os
from typing import Optional, Tuple
import numpy as np

class DetectionIntegrator:
    def __init__(self, sector: str, db: Optional[SafetyDB] = None):
        self.db = db or SafetyDB()
        self.sector = sector

    def _determine_severity(self, confidence: float, incident_type: IncidentType) -> Severity:
        """Determine incident severity based on confidence score and type"""
        if incident_type == IncidentType.FIRE:
            if confidence > 0.9:
                return Severity.CRITICAL
            elif confidence > 0.7:
                return Severity.HIGH
            elif confidence > 0.5:
                return Severity.MEDIUM
            return Severity.LOW
        
        elif incident_type == IncidentType.FALL:
            if confidence > 0.85:
                return Severity.HIGH
            elif confidence > 0.6:
                return Severity.MEDIUM
            return Severity.LOW
        
        else:  # PPE_VIOLATION
            if confidence > 0.95:
                return Severity.HIGH
            elif confidence > 0.75:
                return Severity.MEDIUM
            return Severity.LOW

    def _save_detection_image(self, frame: np.ndarray, incident_type: str) -> str:
        """Save the detection frame as an image"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"detection_{incident_type}_{timestamp}.jpg"
        save_path = os.path.join("incident_tracker", "detections", filename)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        # Assuming frame is a numpy array from OpenCV
        # cv2.imwrite(save_path, frame)
        return save_path

    def log_fire_detection(self, confidence: float, frame: Optional[np.ndarray] = None,
                         video_path: Optional[str] = None) -> str:
        """Log a fire detection incident"""
        image_path = self._save_detection_image(frame, "fire") if frame is not None else None
        
        incident = Incident(
            incident_type=IncidentType.FIRE,
            timestamp=datetime.now(),
            sector=self.sector,
            severity=self._determine_severity(confidence, IncidentType.FIRE),
            description=f"Fire detected with {confidence:.2%} confidence",
            image_path=image_path,
            video_path=video_path,
            confidence_score=confidence
        )
        
        return self.db.log_incident(incident)

    def log_fall_detection(self, confidence: float, frame: Optional[np.ndarray] = None,
                         video_path: Optional[str] = None) -> str:
        """Log a fall detection incident"""
        image_path = self._save_detection_image(frame, "fall") if frame is not None else None
        
        incident = Incident(
            incident_type=IncidentType.FALL,
            timestamp=datetime.now(),
            sector=self.sector,
            severity=self._determine_severity(confidence, IncidentType.FALL),
            description=f"Fall detected with {confidence:.2%} confidence",
            image_path=image_path,
            video_path=video_path,
            confidence_score=confidence
        )
        
        return self.db.log_incident(incident)

    def log_ppe_violation(self, missing_items: list, confidence: float,
                         frame: Optional[np.ndarray] = None,
                         video_path: Optional[str] = None) -> str:
        """Log a PPE violation incident"""
        image_path = self._save_detection_image(frame, "ppe") if frame is not None else None
        
        description = f"PPE violation detected: Missing {', '.join(missing_items)}"
        incident = Incident(
            incident_type=IncidentType.PPE_VIOLATION,
            timestamp=datetime.now(),
            sector=self.sector,
            severity=self._determine_severity(confidence, IncidentType.PPE_VIOLATION),
            description=description,
            image_path=image_path,
            video_path=video_path,
            confidence_score=confidence
        )
        
        return self.db.log_incident(incident) 