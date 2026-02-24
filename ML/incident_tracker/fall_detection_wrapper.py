import cv2
import torch
import sys
from pathlib import Path
from detection_integration import DetectionIntegrator

# Add YOLOv5 to path
YOLO_PATH = Path("Image-based-Human-Fall-Detection")
if str(YOLO_PATH) not in sys.path:
    sys.path.append(str(YOLO_PATH))

from models.common import DetectMultiBackend
from utils.general import check_img_size, non_max_suppression, scale_coords
from utils.torch_utils import select_device
from utils.plots import Annotator, colors
from utils.dataloaders import LoadImages, LoadStreams

class FallDetectionWrapper:
    def __init__(self, weights_path='Image-based-Human-Fall-Detection/best.pt', sector="default", device='', conf_thres=0.60):
        """
        Initialize the fall detection wrapper
        
        Args:
            weights_path: Path to the YOLOv5 weights file
            sector: The sector/area being monitored
            device: Device to run inference on ('cpu' or cuda device)
            conf_thres: Confidence threshold for detections (increased to 0.60)
        """
        # Initialize device and model
        self.device = select_device(device)
        self.model = DetectMultiBackend(weights_path, device=self.device)
        self.stride = self.model.stride
        self.names = ['fall detected', 'walking', 'sitting']  # Class names
        self.pt = self.model.pt
        self.imgsz = check_img_size((640, 640), s=self.stride)
        
        # Initialize incident integrator
        self.integrator = DetectionIntegrator(sector=sector)
        self.conf_thres = conf_thres
        self.iou_thres = 0.45
        self.last_alert_time = {}  # To prevent alert spam
    
    def process_video(self, input_path, output_path=None, show_video=False):
        """
        Process a video file for fall detection
        
        Args:
            input_path: Path to input video file
            output_path: Path to save output video (optional)
            show_video: Whether to show video output
        """
        # Load video
        dataset = LoadImages(input_path, img_size=self.imgsz, stride=self.stride, auto=self.pt)
        
        # Video writer setup
        vid_writer = None
        if output_path:
            fps = dataset.fps if hasattr(dataset, 'fps') else 30
            w = int(dataset.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(dataset.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            vid_writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
        
        for path, im, im0s, vid_cap, s in dataset:
            # Prepare image
            im = torch.from_numpy(im).to(self.device)
            im = im.half() if self.model.fp16 else im.float()
            im /= 255
            if len(im.shape) == 3:
                im = im[None]
            
            # Inference
            pred = self.model(im, augment=False, visualize=False)
            pred = non_max_suppression(pred, self.conf_thres, self.iou_thres)
            
            # Process detections
            for i, det in enumerate(pred):
                im0 = im0s.copy()
                annotator = Annotator(im0)
                
                if len(det):
                    # Rescale boxes from img_size to im0 size
                    det[:, :4] = scale_coords(im.shape[2:], det[:, :4], im0.shape).round()
                    
                    # Debug: Print all detections
                    print("\nDetections in frame:")
                    for *xyxy, conf, cls in det:
                        print(f"Class: {self.names[int(cls)]}, Confidence: {conf:.2f}")
                    
                    # Get highest confidence fall detection
                    fall_dets = det[det[:, -1] == 0]  # Class 0 is 'fall detected'
                    if len(fall_dets):
                        max_conf_det = fall_dets[fall_dets[:, 4].argmax()]
                        conf = float(max_conf_det[4])
                        print(f"Found fall with confidence: {conf:.2f}")
                        
                        # Log incident if confidence is high enough
                        if conf >= self.conf_thres:
                            print(f"Logging fall incident (confidence: {conf:.2f})")
                            self.integrator.log_fall_detection(
                                confidence=conf,
                                frame=im0,
                                video_path=input_path
                            )
                    
                    # Draw boxes
                    for *xyxy, conf, cls in reversed(det):
                        c = int(cls)
                        label = f'{self.names[c]} {conf:.2f}'
                        annotator.box_label(xyxy, label, color=colors(c, True))
                
                # Show/save results
                if show_video:
                    cv2.imshow('Fall Detection', im0)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                
                if vid_writer is not None:
                    vid_writer.write(im0)
        
        # Cleanup
        if vid_writer is not None:
            vid_writer.release()
        cv2.destroyAllWindows()
    
    def process_stream(self, source=0):
        """
        Process a live video stream for fall detection
        
        Args:
            source: Camera index or IP camera URL (0 for default webcam)
        """
        dataset = LoadStreams(source, img_size=self.imgsz, stride=self.stride, auto=self.pt)
        
        for path, im, im0s, vid_cap, s in dataset:
            # Prepare image
            im = torch.from_numpy(im).to(self.device)
            im = im.half() if self.model.fp16 else im.float()
            im /= 255
            if len(im.shape) == 3:
                im = im[None]
            
            # Inference
            pred = self.model(im, augment=False, visualize=False)
            pred = non_max_suppression(pred, self.conf_thres, self.iou_thres)
            
            # Process detections
            for i, det in enumerate(pred):
                im0 = im0s[i].copy()
                annotator = Annotator(im0)
                
                if len(det):
                    # Rescale boxes
                    det[:, :4] = scale_coords(im.shape[2:], det[:, :4], im0.shape).round()
                    
                    # Debug: Print all detections
                    print("\nDetections in frame:")
                    for *xyxy, conf, cls in det:
                        print(f"Class: {self.names[int(cls)]}, Confidence: {conf:.2f}")
                    
                    # Get highest confidence fall detection
                    fall_dets = det[det[:, -1] == 0]  # Class 0 is 'fall detected'
                    if len(fall_dets):
                        max_conf_det = fall_dets[fall_dets[:, 4].argmax()]
                        conf = float(max_conf_det[4])
                        print(f"Found fall with confidence: {conf:.2f}")
                        
                        # Log incident if confidence is high enough
                        if conf >= self.conf_thres:
                            print(f"Logging fall incident (confidence: {conf:.2f})")
                            self.integrator.log_fall_detection(
                                confidence=conf,
                                frame=im0
                            )
                    
                    # Draw boxes
                    for *xyxy, conf, cls in reversed(det):
                        c = int(cls)
                        label = f'{self.names[c]} {conf:.2f}'
                        annotator.box_label(xyxy, label, color=colors(c, True))
                
                # Show results
                cv2.imshow(str(i), im0)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    raise StopIteration
        
        cv2.destroyAllWindows() 