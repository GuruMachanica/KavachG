import cv2
import torch
import sys
from pathlib import Path
from datetime import datetime
from pymongo import MongoClient
import logging
import os
from typing import Optional, Tuple, List

# Configure logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    filename='logs/safety_system.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def safe_load_model(weights_path: str, device):
    """Safely load model weights with PyTorch version compatibility"""
    try:
        # First try loading with default settings
        return torch.load(weights_path, map_location=device)
    except Exception as e:
        logging.warning(f"Standard loading failed, trying alternative method: {str(e)}")
        try:
            # Try loading with pickle_module=None for older PyTorch versions
            return torch.load(weights_path, map_location=device, pickle_module=None)
        except Exception as e:
            logging.error(f"All loading methods failed: {str(e)}")
            raise

class SafetySystem:
    def __init__(self, 
                 sector: str = "default",
                 mongodb_uri: str = "mongodb://localhost:27017/",
                 fire_weights: str = 'yolov5-fire-detection/models/FinalFireSmoke/weights/best.pt',
                 fall_weights: str = 'Image-based-Human-Fall-Detection/best.pt',
                 device: str = ''):
        """
        Unified safety system that handles both ML detection and database operations
        """
        self.sector = sector
        
        # Add YOLO paths to system path
        fire_path = Path("yolov5-fire-detection/yolov5")
        fall_path = Path("Image-based-Human-Fall-Detection")
        
        if str(fire_path) not in sys.path:
            sys.path.append(str(fire_path))
        if str(fall_path) not in sys.path:
            sys.path.append(str(fall_path))
        
        # Verify model paths exist
        self._verify_paths(fire_weights, fall_weights)
        
        # Setup components
        self._setup_directories()
        self.setup_database(mongodb_uri)
        self.setup_models(fire_weights, fall_weights, device)
        
        logging.info(f"SafetySystem initialized for sector: {sector}")
    
    def _verify_paths(self, fire_weights: str, fall_weights: str):
        """Verify that model weights exist"""
        if not os.path.exists(fire_weights):
            raise FileNotFoundError(f"Fire detection weights not found at: {fire_weights}")
        if not os.path.exists(fall_weights):
            raise FileNotFoundError(f"Fall detection weights not found at: {fall_weights}")
    
    def _setup_directories(self):
        """Create necessary directories"""
        os.makedirs('detections', exist_ok=True)
        os.makedirs('detections/fire', exist_ok=True)
        os.makedirs('detections/fall', exist_ok=True)
        
    def setup_database(self, mongodb_uri: str):
        """Initialize database connection with retry logic"""
        max_retries = 3
        current_retry = 0
        
        while current_retry < max_retries:
            try:
                self.client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
                # Verify connection
                self.client.server_info()
                self.db = self.client.safety_monitoring
                self.collection = self.db.incidents
                
                # Create indexes
                self.collection.create_index([("timestamp", -1)])
                self.collection.create_index([("incident_type", 1)])
                self.collection.create_index([("sector", 1)])
                
                logging.info(f"Connected to MongoDB for sector: {self.sector}")
                break
                
            except Exception as e:
                current_retry += 1
                if current_retry == max_retries:
                    logging.error(f"Failed to connect to MongoDB after {max_retries} attempts: {str(e)}")
                    raise
                logging.warning(f"Database connection attempt {current_retry} failed, retrying...")

    def setup_models(self, fire_weights: str, fall_weights: str, device: str):
        """Initialize ML models with proper path handling"""
        try:
            from models.common import DetectMultiBackend
            from utils.torch_utils import select_device
            from models.yolo import Model  # Import YOLO model class
            
            self.device = select_device(device)
            
            # Initialize models with error checking and safe loading
            try:
                self.fire_model = DetectMultiBackend(fire_weights, device=self.device)
                if hasattr(self.fire_model, 'model'):
                    self.fire_model.model.half() if self.fire_model.fp16 else self.fire_model.model.float()
                self.fire_model.eval()
                logging.info("Fire detection model loaded successfully")
            except Exception as e:
                logging.error(f"Failed to load fire detection model: {str(e)}")
                raise
                
            try:
                self.fall_model = DetectMultiBackend(fall_weights, device=self.device)
                if hasattr(self.fall_model, 'model'):
                    self.fall_model.model.half() if self.fall_model.fp16 else self.fall_model.model.float()
                self.fall_model.eval()
                logging.info("Fall detection model loaded successfully")
            except Exception as e:
                logging.error(f"Failed to load fall detection model: {str(e)}")
                raise
            
        except Exception as e:
            logging.error(f"Model initialization failed: {str(e)}")
            raise

    def process_frame(self, frame, conf_threshold: float = 0.25) -> Tuple[List[dict], List[dict]]:
        """Process a single frame for both fire and fall detection"""
        if frame is None or frame.size == 0:
            logging.error("Received invalid frame")
            return [], []
            
        try:
            # Ensure frame is in correct format
            if len(frame.shape) != 3:
                logging.error("Invalid frame format - expected 3 channels")
                return [], []
                
            # Prepare frame for inference
            img = self.prepare_image(frame)
            
            # Fire detection with error handling
            try:
                with torch.no_grad():
                    fire_pred = self.fire_model(img)
                    fire_dets = self.process_predictions(fire_pred, conf_threshold, "fire")
            except Exception as e:
                logging.error(f"Fire detection failed: {str(e)}")
                fire_dets = []
            
            # Fall detection with error handling
            try:
                with torch.no_grad():
                    fall_pred = self.fall_model(img)
                    fall_dets = self.process_predictions(fall_pred, conf_threshold, "fall")
            except Exception as e:
                logging.error(f"Fall detection failed: {str(e)}")
                fall_dets = []
            
            return fire_dets, fall_dets
            
        except Exception as e:
            logging.error(f"Frame processing error: {str(e)}")
            return [], []

    def prepare_image(self, frame):
        """Prepare image for model inference"""
        try:
            # Convert frame to RGB if necessary
            if frame.shape[2] == 4:  # Handle RGBA images
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            
            # Resize with interpolation method
            img = cv2.resize(frame, (640, 640), interpolation=cv2.INTER_LINEAR)
            img = img.transpose(2, 0, 1)  # HWC to CHW
            img = torch.from_numpy(img).to(self.device)
            img = img.half() if self.fire_model.fp16 else img.float()
            img /= 255.0
            if len(img.shape) == 3:
                img = img[None]
            return img
        except Exception as e:
            logging.error(f"Image preparation error: {str(e)}")
            raise

    def process_predictions(self, pred, conf_threshold: float, detection_type: str) -> List[dict]:
        """Process model predictions and return detections"""
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
                
                # Log significant detections to MongoDB with cooldown
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
                if cv2.getWindowProperty('Safety Monitoring', cv2.WND_PROP_VISIBLE) < 1:
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

    def log_detection(self, detection: dict, frame) -> Optional[str]:
        """Log a detection to the database with validation"""
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
            
            # Create incident document
            incident = {
                'incident_type': detection['type'],
                'timestamp': datetime.now(),
                'sector': self.sector,
                'severity': self.determine_severity(detection['confidence'], detection['type']),
                'confidence_score': float(detection['confidence']),  # Ensure float
                'image_path': image_path,
                'description': f"{detection['type'].capitalize()} detected with {detection['confidence']:.2%} confidence"
            }
            
            # Insert into database with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    result = self.collection.insert_one(incident)
                    incident_id = str(result.inserted_id)
                    logging.info(f"Logged {detection['type']} incident: {incident_id}")
                    return incident_id
                except Exception as e:
                    if attempt == max_retries - 1:
                        logging.error(f"Failed to log detection after {max_retries} attempts: {str(e)}")
                        return None
                    continue
            
        except Exception as e:
            logging.error(f"Failed to log detection: {str(e)}")
            return None

    def determine_severity(self, confidence: float, incident_type: str) -> str:
        """Determine incident severity based on confidence and type"""
        try:
            if incident_type == "fire":
                if confidence > 0.9: return "critical"
                elif confidence > 0.7: return "high"
                elif confidence > 0.5: return "medium"
                return "low"
            else:  # fall
                if confidence > 0.85: return "high"
                elif confidence > 0.6: return "medium"
                return "low"
        except Exception as e:
            logging.error(f"Error determining severity: {str(e)}")
            return "low"

    def __del__(self):
        """Cleanup resources"""
        try:
            self.client.close()
            logging.info("Safety system shutdown complete")
        except:
            pass 