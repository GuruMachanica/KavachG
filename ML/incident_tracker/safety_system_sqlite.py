import os
import cv2
import torch
import logging
import numpy as np
import sqlite3
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/safety_system.log'),
        logging.StreamHandler()
    ]
)

def safe_load_model(weights_path: str, device):
    """Safely load a PyTorch model with error handling"""
    try:
        if not os.path.exists(weights_path):
            raise FileNotFoundError(f"Model weights not found at: {weights_path}")
        
        model = torch.hub.load('yolov5-fire-detection/yolov5', 'custom', 
                               path=weights_path, source='local', device=device)
        return model
    except Exception as e:
        logging.error(f"Error loading model from {weights_path}: {str(e)}")
        raise

class SafetySystem:
    """Safety monitoring system to detect incidents in videos"""
    
    def __init__(self, 
                 sector: str = "default",
                 db_path: str = 'safety_monitoring.sqlite',
                 fire_weights: str = 'yolov5-fire-detection/models/FinalFireSmoke/weights/best.pt',
                 fall_weights: str = 'Image-based-Human-Fall-Detection/best.pt',
                 device: str = ''):
        """
        Initialize the safety system
        
        Args:
            sector: Name of the sector being monitored
            db_path: Path to SQLite database
            fire_weights: Path to the fire detection model weights
            fall_weights: Path to the fall detection model weights
            device: Device to run inference on ('cpu', '0', '0,1', etc.)
        """
        self.sector = sector
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
        # Verify paths
        self._verify_paths(fire_weights, fall_weights)
        
        # Set up directories
        self._setup_directories()
        
        # Set up database
        self.setup_database(db_path)
        
        # Initialize models
        self.setup_models(fire_weights, fall_weights, device)
        
        logging.info(f"SafetySystem initialized for sector: {sector}")
        print(f"SafetySystem initialized for sector: {sector}")
    
    def _verify_paths(self, fire_weights: str, fall_weights: str):
        """Verify model paths exist"""
        for path in [fire_weights, fall_weights]:
            if not os.path.exists(path):
                logging.warning(f"Model weights not found at: {path}")
    
    def _setup_directories(self):
        """Set up required directories"""
        for dir_path in ['logs', 'detections/fire', 'detections/fall']:
            os.makedirs(dir_path, exist_ok=True)
    
    def setup_database(self, db_path: str):
        """Set up SQLite database connection"""
        try:
            self.conn = sqlite3.connect(db_path)
            self.cursor = self.conn.cursor()
            
            # Create incidents table if it doesn't exist
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                sector TEXT NOT NULL,
                severity TEXT NOT NULL,
                confidence_score REAL NOT NULL,
                image_path TEXT,
                description TEXT,
                status TEXT DEFAULT 'detected',
                resolution_notes TEXT,
                resolution_time TEXT
            )
            ''')
            self.conn.commit()
            logging.info(f"Connected to SQLite database at {db_path}")
            
        except Exception as e:
            logging.error(f"Database connection error: {str(e)}")
            raise
    
    def setup_models(self, fire_weights: str, fall_weights: str, device: str):
        """Set up detection models"""
        try:
            # Determine device
            if not device:
                device = 'cuda' if torch.cuda.is_available() else 'cpu'
            
            # Load fire detection model
            self.fire_model = safe_load_model(fire_weights, device)
            logging.info("Fire detection model loaded successfully")
            print("Fire detection model loaded successfully")
            
            # Load fall detection model
            self.fall_model = safe_load_model(fall_weights, device)
            logging.info("Fall detection model loaded successfully")
            print("Fall detection model loaded successfully")
            
        except Exception as e:
            logging.error(f"Error setting up models: {str(e)}")
            raise
    
    def process_frame(self, frame, conf_threshold: float = 0.25) -> Tuple[List[dict], List[dict]]:
        """Process a single frame for both fire and fall detection"""
        if frame is None:
            logging.warning("Received empty frame")
            return [], []
        
        try:
            # Prepare image for model
            img = self.prepare_image(frame)
            
            # Fire detection
            fire_pred = self.fire_model(img)
            fire_dets = self.process_predictions(fire_pred, conf_threshold, 'fire')
            
            # Fall detection
            fall_pred = self.fall_model(img)
            fall_dets = self.process_predictions(fall_pred, conf_threshold, 'fall')
            
            return fire_dets, fall_dets
            
        except Exception as e:
            logging.error(f"Error processing frame: {str(e)}")
            return [], []
    
    def prepare_image(self, frame):
        """Prepare image for model inference"""
        try:
            # Return the raw frame for YOLOv5 model which handles preprocessing
            return frame
        except Exception as e:
            logging.error(f"Error preparing image: {str(e)}")
            return frame
    
    def process_predictions(self, pred, conf_threshold: float, detection_type: str) -> List[dict]:
        """Process model predictions and convert to standardized format"""
        detections = []
        try:
            if pred[0] is not None and len(pred[0]):
                # Convert predictions to numpy for easier handling
                pred_boxes = pred[0].cpu().numpy()
                
                for det in pred_boxes:
                    if len(det) >= 6:  # box coordinates (4) + confidence (1) + class (1)
                        conf = float(det[4])
                        if conf >= conf_threshold:
                            # Extract box coordinates
                            box = det[:4].tolist()
                            detections.append({
                                'box': box,
                                'confidence': conf,
                                'class': int(det[5]),
                                'type': detection_type
                            })
                            
        except Exception as e:
            logging.error(f"Error processing predictions: {str(e)}")
        return detections

    def display_frame(self, frame, detections):
        """Display frame with detection boxes and info"""
        try:
            # Create a copy for display
            display_frame = frame.copy()
            
            # Add detection boxes and labels
            for det in detections:
                if det['confidence'] > 0.25:  # Lower threshold for display
                    box = det['box']
                    if len(box) != 4:
                        logging.warning(f"Invalid box format: {box}")
                        continue
                        
                    # Ensure box coordinates are within frame boundaries and convert to integers
                    h, w = frame.shape[:2]
                    x1 = max(0, min(w, int(round(box[0]))))
                    y1 = max(0, min(h, int(round(box[1]))))
                    x2 = max(0, min(w, int(round(box[2]))))
                    y2 = max(0, min(h, int(round(box[3]))))
                    
                    # Skip if box is invalid
                    if x1 >= x2 or y1 >= y2:
                        continue
                    
                    color = (0, 0, 255) if det['type'] == 'fire' else (255, 0, 0)
                    cv2.rectangle(display_frame, (x1, y1), (x2, y2), color, 2)
                    
                    # Add detection label with confidence
                    label = f"{det['type'].upper()}: {det['confidence']:.2f}"
                    # Ensure label position is within frame
                    label_y = max(30, y1 - 10)
                    cv2.putText(display_frame, label, (x1, label_y),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Add border and status text
            border_size = 30
            display_frame = cv2.copyMakeBorder(display_frame, border_size, border_size, border_size, border_size, 
                                             cv2.BORDER_CONSTANT, value=(0, 0, 0))
            
            status_text = "Safety Monitoring System - Press Q to quit"
            cv2.putText(display_frame, status_text, (40, 25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Create and position window
            cv2.namedWindow('Safety Monitoring', cv2.WINDOW_NORMAL)
            cv2.moveWindow('Safety Monitoring', 100, 100)
            cv2.imshow('Safety Monitoring', display_frame)
            
        except Exception as e:
            logging.error(f"Display error: {str(e)}")
            # Continue execution even if display fails
            pass

    def process_video(self, source_path: str, show_output: bool = False):
        """Process a video file for both fire and fall detection"""
        try:
            # Handle both file paths and camera indices
            source = int(source_path) if source_path.isdigit() else source_path
            cap = cv2.VideoCapture(source)
            
            if not cap.isOpened():
                raise ValueError(f"Failed to open video source: {source_path}")
            
            # Get video properties
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            print(f"\nVideo Properties:")
            print(f"Resolution: {width}x{height}")
            print(f"FPS: {fps}")
            print(f"Total Frames: {total_frames}")
            print("Starting video processing...\n")
            
            frame_count = 0
            last_detection_time = {}  # Track last detection time for each type
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("\nEnd of video")
                    break
                
                frame_count += 1
                if frame_count % 30 == 0:
                    print(f"Processing frame {frame_count}/{total_frames}")
                
                # Process frame for detections - using lower confidence threshold
                fire_dets, fall_dets = self.process_frame(frame, conf_threshold=0.25)
                
                current_time = datetime.now()
                
                # Log significant detections with cooldown
                for det in fire_dets + fall_dets:
                    if det['confidence'] > 0.25:  # Lower confidence threshold for logging
                        # Check if enough time has passed since last detection of this type
                        if det['type'] not in last_detection_time or \
                           (current_time - last_detection_time[det['type']]).total_seconds() > 2:
                            
                            incident_id = self.log_detection(det, frame)
                            if incident_id:
                                last_detection_time[det['type']] = current_time
                                print(f"\nLogged {det['type']} incident:")
                                print(f"- ID: {incident_id}")
                                print(f"- Confidence: {det['confidence']:.2f}")
                                print(f"- Severity: {self.determine_severity(det['confidence'], det['type'])}")
                
                # Display output if requested
                if show_output:
                    self.display_frame(frame, fire_dets + fall_dets)
                    key = cv2.waitKey(max(1, int(1000/fps))) & 0xFF  # Maintain video FPS
                    if key == ord('q'):
                        print("\nUser requested quit")
                        break
                
                # Check if window was closed
                if show_output and cv2.getWindowProperty('Safety Monitoring', cv2.WND_PROP_VISIBLE) < 1:
                    print("\nWindow closed by user")
                    break
            
            cap.release()
            cv2.destroyAllWindows()
            print(f"\nProcessing completed:")
            print(f"Total frames processed: {frame_count}")
            
        except Exception as e:
            print(f"Error in video processing: {str(e)}")
            logging.error(f"Video processing error: {str(e)}")
            raise
        finally:
            try:
                cap.release()
                cv2.destroyAllWindows()
            except:
                pass

    def log_detection(self, detection: dict, frame) -> Optional[int]:
        """Log a detection to the SQLite database with validation"""
        try:
            # Validate detection
            if not isinstance(detection, dict) or 'confidence' not in detection:
                logging.error("Invalid detection format")
                return None
            
            # Create timestamped filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            image_path = f"detections/{detection['type']}/{timestamp}.jpg"
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(image_path), exist_ok=True)
            
            # Save detection image
            try:
                cv2.imwrite(image_path, frame)
            except Exception as e:
                logging.error(f"Failed to save detection image: {str(e)}")
                image_path = None
            
            # Calculate severity
            severity = self.determine_severity(detection['confidence'], detection['type'])
            
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            description = f"{detection['type'].capitalize()} detected with {detection['confidence']:.2%} confidence"
            
            # Insert into database with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    if self.conn is None:
                        self.setup_database(self.db_path)
                    
                    self.cursor.execute('''
                    INSERT INTO incidents 
                    (incident_type, timestamp, sector, severity, confidence_score, image_path, description) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        detection['type'],
                        current_time,
                        self.sector,
                        severity,
                        float(detection['confidence']),
                        image_path,
                        description
                    ))
                    
                    self.conn.commit()
                    incident_id = self.cursor.lastrowid
                    return incident_id
                    
                except sqlite3.Error as e:
                    logging.error(f"Database error (attempt {attempt+1}/{max_retries}): {str(e)}")
                    if attempt == max_retries - 1:
                        return None
                    
                    # Try to reconnect
                    try:
                        self.conn.close()
                    except:
                        pass
                    self.setup_database(self.db_path)
            
            return None
            
        except Exception as e:
            logging.error(f"Error logging detection: {str(e)}")
            return None

    def determine_severity(self, confidence: float, incident_type: str) -> str:
        """Determine severity based on confidence score and incident type"""
        if incident_type == 'fire':
            if confidence > 0.65: return 'high'
            elif confidence > 0.45: return 'medium'
            else: return 'low'
        elif incident_type == 'fall':
            if confidence > 0.75: return 'high'
            elif confidence > 0.50: return 'medium'
            else: return 'low'
        else:
            if confidence > 0.70: return 'high'
            elif confidence > 0.50: return 'medium'
            else: return 'low'

    def __del__(self):
        """Clean up resources on destruction"""
        if self.conn:
            try:
                self.conn.close()
            except:
                pass
        print("Safety system shutdown complete") 