import cv2
import torch
from pathlib import Path
from detection_integration import DetectionIntegrator
from ultralytics import YOLO

class PPEDetectionWrapper:
    def __init__(self, weights_path='Construction-Site-Safety-PPE-Detection/models/best.pt', 
                 sector="default", conf_thres=0.25):
        """
        Initialize the PPE detection wrapper
        
        Args:
            weights_path: Path to the YOLOv8 weights file
            sector: The sector/area being monitored
            conf_thres: Confidence threshold for detections
        """
        # Load the YOLOv8 model
        self.model = YOLO(weights_path)
        
        # Initialize incident integrator
        self.integrator = DetectionIntegrator(sector=sector)
        self.conf_thres = conf_thres
        
        # Class mapping (based on the dataset's classes)
        self.class_names = [
            'Hardhat', 'Mask', 'NO-Hardhat', 'NO-Mask', 'NO-Safety Vest',
            'Person', 'Safety Cone', 'Safety Vest', 'machinery', 'vehicle'
        ]
        
        # Required PPE mapping
        self.required_ppe = {
            'Hardhat': ['NO-Hardhat'],
            'Mask': ['NO-Mask'],
            'Safety Vest': ['NO-Safety Vest']
        }
    
    def _check_ppe_violations(self, detections):
        """
        Check for PPE violations in the detections
        
        Returns:
            tuple: (has_violations, missing_items, confidence)
        """
        violations = []
        max_conf = 0.0
        
        # Track detected items
        detected_items = {cls: False for cls in self.class_names}
        for detection in detections:
            cls = self.class_names[int(detection.cls)]
            conf = float(detection.conf)
            detected_items[cls] = True
            
            # Update confidence for violation detections
            if cls.startswith('NO-') and conf > max_conf:
                max_conf = conf
        
        # Check for violations
        for required, violations_list in self.required_ppe.items():
            for violation in violations_list:
                if detected_items[violation]:
                    violations.append(required)
        
        return bool(violations), violations, max_conf
    
    def process_video(self, input_path, output_path=None, show_video=False):
        """
        Process a video file for PPE violations
        
        Args:
            input_path: Path to input video file
            output_path: Path to save output video (optional)
            show_video: Whether to show video output
        """
        # Open video file
        cap = cv2.VideoCapture(input_path)
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Setup video writer if output path is provided
        out = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Perform inference
            results = self.model(frame, conf=self.conf_thres)[0]
            
            # Check for PPE violations
            has_violations, missing_items, max_conf = self._check_ppe_violations(results.boxes)
            
            # Log incident if violations are detected
            if has_violations:
                self.integrator.log_ppe_violation(
                    missing_items=missing_items,
                    confidence=max_conf,
                    frame=frame,
                    video_path=input_path
                )
            
            # Get annotated frame
            annotated_frame = results.plot()
            
            # Show/save results
            if show_video:
                cv2.imshow('PPE Detection', annotated_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            if out is not None:
                out.write(annotated_frame)
        
        # Cleanup
        cap.release()
        if out is not None:
            out.release()
        cv2.destroyAllWindows()
    
    def process_stream(self, source=0):
        """
        Process a live video stream for PPE violations
        
        Args:
            source: Camera index or IP camera URL (0 for default webcam)
        """
        cap = cv2.VideoCapture(source)
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Perform inference
            results = self.model(frame, conf=self.conf_thres)[0]
            
            # Check for PPE violations
            has_violations, missing_items, max_conf = self._check_ppe_violations(results.boxes)
            
            # Log incident if violations are detected
            if has_violations:
                self.integrator.log_ppe_violation(
                    missing_items=missing_items,
                    confidence=max_conf,
                    frame=frame
                )
            
            # Get annotated frame
            annotated_frame = results.plot()
            
            # Show results
            cv2.imshow('PPE Detection', annotated_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # Cleanup
        cap.release()
        cv2.destroyAllWindows() 