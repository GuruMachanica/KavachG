import argparse
import cv2
import torch
import os
import sys
import numpy as np
import time
from datetime import datetime
import logging
import pymongo
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/all_detectors.log'),
        logging.StreamHandler()
    ]
)

class AllInOneDetector:
    def __init__(self, 
                 sector='default',
                 mongodb_uri='mongodb://localhost:27017/'):
        """Initialize the detector with all three models"""
        self.sector = sector
        
        # Setup directories
        os.makedirs('detections/fire', exist_ok=True)
        os.makedirs('detections/fall', exist_ok=True)
        os.makedirs('detections/ppe', exist_ok=True)
        
        # Connect to MongoDB
        try:
            self.client = pymongo.MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
            self.db = self.client.safety_monitoring
            self.collection = self.db.incidents
            logging.info(f"Connected to MongoDB at {mongodb_uri}")
        except Exception as e:
            logging.error(f"MongoDB connection error: {str(e)}")
            raise
            
        # Load the models
        self.load_models()
        
        logging.info(f"AllInOneDetector initialized for sector: {sector}")
        
    def load_models(self):
        """Load all three detection models"""
        try:
            # Dynamically import YOLOv5 modules
            sys.path.append(os.path.join(os.getcwd(), 'yolov5-fire-detection/yolov5'))
            from models.common import DetectMultiBackend
            from utils.general import check_img_size
            from utils.torch_utils import select_device
            
            # Set device
            self.device = select_device('')
            
            # Load Fire Detection Model
            fire_weights = 'yolov5-fire-detection/models/FinalFireSmoke/weights/best.pt'
            self.fire_model = DetectMultiBackend(fire_weights, device=self.device)
            if hasattr(self.fire_model, 'stride'):
                self.fire_size = check_img_size((640, 640), s=self.fire_model.stride)
            else:
                self.fire_size = (640, 640)
            self.fire_model.eval()
            logging.info("Fire detection model loaded")
            
            # Load Fall Detection Model
            fall_weights = 'Image-based-Human-Fall-Detection/best.pt'
            self.fall_model = DetectMultiBackend(fall_weights, device=self.device)
            if hasattr(self.fall_model, 'stride'):
                self.fall_size = check_img_size((640, 640), s=self.fall_model.stride)
            else:
                self.fall_size = (640, 640)
            self.fall_model.eval()
            logging.info("Fall detection model loaded")
            
            # Load PPE Detection Model (if available)
            ppe_weights = 'models/best.pt'
            if os.path.exists(ppe_weights):
                self.ppe_model = DetectMultiBackend(ppe_weights, device=self.device)
                if hasattr(self.ppe_model, 'stride'):
                    self.ppe_size = check_img_size((640, 640), s=self.ppe_model.stride)
                else:
                    self.ppe_size = (640, 640)
                self.ppe_model.eval()
                self.has_ppe_model = True
                logging.info("PPE detection model loaded")
            else:
                self.has_ppe_model = False
                logging.warning("PPE detection model not found")
                
        except Exception as e:
            logging.error(f"Error loading models: {str(e)}")
            raise
    
    def preprocess_image(self, frame, target_size):
        """Preprocess image for model inference"""
        img = cv2.resize(frame, target_size, interpolation=cv2.INTER_LINEAR)
        img = img.transpose(2, 0, 1)  # HWC to CHW
        img = np.ascontiguousarray(img)
        img = torch.from_numpy(img).to(self.device)
        img = img.float() / 255.0
        if len(img.shape) == 3:
            img = img[None]
        return img
    
    def detect_fire(self, frame, conf_threshold=0.25):
        """Detect fire in a frame"""
        try:
            img = self.preprocess_image(frame, self.fire_size)
            pred = self.fire_model(img)
            detections = []
            
            if pred[0] is not None and len(pred[0]):
                boxes = pred[0][:, :4].cpu().numpy()
                confidences = pred[0][:, 4].cpu().numpy()
                classes = pred[0][:, 5].cpu().numpy()
                
                for box, conf, cls in zip(boxes, confidences, classes):
                    if conf >= conf_threshold:
                        detections.append({
                            'box': box.tolist(),
                            'confidence': float(conf),
                            'class': int(cls),
                            'type': 'fire'
                        })
            
            return detections
        except Exception as e:
            logging.error(f"Fire detection error: {str(e)}")
            return []
    
    def detect_fall(self, frame, conf_threshold=0.25):
        """Detect falls in a frame"""
        try:
            img = self.preprocess_image(frame, self.fall_size)
            pred = self.fall_model(img)
            detections = []
            
            if pred[0] is not None and len(pred[0]):
                boxes = pred[0][:, :4].cpu().numpy()
                confidences = pred[0][:, 4].cpu().numpy()
                classes = pred[0][:, 5].cpu().numpy()
                
                for box, conf, cls in zip(boxes, confidences, classes):
                    if conf >= conf_threshold:
                        detections.append({
                            'box': box.tolist(),
                            'confidence': float(conf),
                            'class': int(cls),
                            'type': 'fall'
                        })
            
            return detections
        except Exception as e:
            logging.error(f"Fall detection error: {str(e)}")
            return []
    
    def detect_ppe(self, frame, conf_threshold=0.25):
        """Detect PPE in a frame"""
        if not self.has_ppe_model:
            return []
            
        try:
            img = self.preprocess_image(frame, self.ppe_size)
            pred = self.ppe_model(img)
            detections = []
            
            if pred[0] is not None and len(pred[0]):
                boxes = pred[0][:, :4].cpu().numpy()
                confidences = pred[0][:, 4].cpu().numpy()
                classes = pred[0][:, 5].cpu().numpy()
                
                for box, conf, cls in zip(boxes, confidences, classes):
                    if conf >= conf_threshold:
                        detections.append({
                            'box': box.tolist(),
                            'confidence': float(conf),
                            'class': int(cls),
                            'type': 'ppe_violation' if cls == 0 else 'ppe_compliance'
                        })
            
            return detections
        except Exception as e:
            logging.error(f"PPE detection error: {str(e)}")
            return []
    
    def log_detection(self, detection, frame):
        """Log detection to MongoDB"""
        try:
            # Create timestamped filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            image_path = f"detections/{detection['type']}/{timestamp}.jpg"
            
            # Save detection image
            os.makedirs(os.path.dirname(image_path), exist_ok=True)
            cv2.imwrite(image_path, frame)
            
            # Determine severity based on type and confidence
            if detection['type'] == 'fire':
                if detection['confidence'] > 0.8:
                    severity = 'critical'
                elif detection['confidence'] > 0.6:
                    severity = 'high'
                elif detection['confidence'] > 0.4:
                    severity = 'medium'
                else:
                    severity = 'low'
            elif detection['type'] == 'fall':
                if detection['confidence'] > 0.7:
                    severity = 'high'
                elif detection['confidence'] > 0.5:
                    severity = 'medium'
                else:
                    severity = 'low'
            else:  # PPE
                if detection['confidence'] > 0.7:
                    severity = 'medium'
                else:
                    severity = 'low'
            
            # Create incident document
            incident = {
                'incident_type': detection['type'],
                'timestamp': datetime.now(),
                'sector': self.sector,
                'severity': severity,
                'confidence_score': detection['confidence'],
                'image_path': image_path,
                'description': f"{detection['type'].capitalize()} detected with {detection['confidence']:.2f} confidence"
            }
            
            # Insert into database
            result = self.collection.insert_one(incident)
            incident_id = str(result.inserted_id)
            
            logging.info(f"Logged {detection['type']} incident: {incident_id}")
            return incident_id
            
        except Exception as e:
            logging.error(f"Error logging detection: {str(e)}")
            return None
    
    def process_frame(self, frame, conf_threshold=0.25):
        """Process a single frame with all detection models"""
        if frame is None or frame.size == 0:
            return []
            
        detections = []
        
        # Run fire detection
        fire_dets = self.detect_fire(frame, conf_threshold)
        detections.extend(fire_dets)
        
        # Run fall detection
        fall_dets = self.detect_fall(frame, conf_threshold)
        detections.extend(fall_dets)
        
        # Run PPE detection if available
        if self.has_ppe_model:
            ppe_dets = self.detect_ppe(frame, conf_threshold)
            detections.extend(ppe_dets)
            
        return detections
    
    def display_frame(self, frame, detections):
        """Display frame with detections"""
        display_frame = frame.copy()
        
        # Draw detection boxes
        for det in detections:
            if det['confidence'] > 0.25:
                box = det['box']
                h, w = frame.shape[:2]
                x1 = max(0, min(w, int(round(box[0]))))
                y1 = max(0, min(h, int(round(box[1]))))
                x2 = max(0, min(w, int(round(box[2]))))
                y2 = max(0, min(h, int(round(box[3]))))
                
                # Skip if box is invalid
                if x1 >= x2 or y1 >= y2:
                    continue
                
                # Color based on detection type
                if det['type'] == 'fire':
                    color = (0, 0, 255)  # Red
                elif det['type'] == 'fall':
                    color = (255, 0, 0)  # Blue
                elif det['type'] == 'ppe_violation':
                    color = (0, 165, 255)  # Orange
                else:
                    color = (0, 255, 0)  # Green
                
                cv2.rectangle(display_frame, (x1, y1), (x2, y2), color, 2)
                
                # Add label
                label = f"{det['type'].upper()}: {det['confidence']:.2f}"
                label_y = max(30, y1 - 10)
                cv2.putText(display_frame, label, (x1, label_y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Add status text
        cv2.putText(display_frame, f"Safety Monitoring - Sector: {self.sector}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Display frame
        cv2.namedWindow('All-In-One Detector', cv2.WINDOW_NORMAL)
        cv2.imshow('All-In-One Detector', display_frame)
    
    def process_video(self, source_path, show_output=True, conf_threshold=0.25):
        """Process video with all detection models"""
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
                    print(f"Processing frame {frame_count}/{total_frames if total_frames > 0 else 'unknown'}")
                
                # Only process every 5th frame to improve performance
                if frame_count % 5 == 0:
                    detections = self.process_frame(frame, conf_threshold)
                    
                    # Log significant detections with cooldown
                    current_time = datetime.now()
                    for det in detections:
                        if det['confidence'] > conf_threshold:
                            det_type = det['type']
                            if det_type not in last_detection_time or \
                               (current_time - last_detection_time[det_type]).total_seconds() > 2:
                                
                                incident_id = self.log_detection(det, frame)
                                if incident_id:
                                    last_detection_time[det_type] = current_time
                                    print(f"\nLogged {det_type} incident:")
                                    print(f"- ID: {incident_id}")
                                    print(f"- Confidence: {det['confidence']:.2f}")
                    
                    # Display output if requested
                    if show_output:
                        self.display_frame(frame, detections)
                
                if show_output:
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q') or key == 27:  # q or ESC
                        print("\nUser requested quit")
                        break
                        
                if show_output and cv2.getWindowProperty('All-In-One Detector', cv2.WND_PROP_VISIBLE) < 1:
                    print("\nWindow closed by user")
                    break
            
            cap.release()
            if show_output:
                cv2.destroyAllWindows()
                
            print(f"\nProcessing completed:")
            print(f"Total frames processed: {frame_count}")
            
        except Exception as e:
            logging.error(f"Video processing error: {str(e)}")
            raise
        finally:
            try:
                cap.release()
                if show_output:
                    cv2.destroyAllWindows()
            except:
                pass
                
    def __del__(self):
        """Clean up resources"""
        try:
            self.client.close()
            logging.info("Detector shutdown complete")
        except:
            pass

def main():
    parser = argparse.ArgumentParser(description='Run the All-In-One Safety Detector')
    parser.add_argument('--source', required=True, help='Path to video file or camera index')
    parser.add_argument('--show', action='store_true', default=True, help='Show output video')
    parser.add_argument('--conf', type=float, default=0.25, help='Confidence threshold (0.0-1.0)')
    parser.add_argument('--sector', default='main', help='Sector name for incident tracking')
    parser.add_argument('--mongodb-uri', default='mongodb://localhost:27017/', help='MongoDB URI')
    
    args = parser.parse_args()
    
    logging.info(f"Starting All-In-One Detector for sector: {args.sector}")
    
    try:
        detector = AllInOneDetector(
            sector=args.sector,
            mongodb_uri=args.mongodb_uri
        )
        
        detector.process_video(
            args.source, 
            show_output=args.show,
            conf_threshold=args.conf
        )
        
    except Exception as e:
        logging.error(f"Error running detector: {str(e)}")
        raise

if __name__ == "__main__":
    main() 