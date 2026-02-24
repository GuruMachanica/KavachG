import sys
import os
from pathlib import Path
import torch
import cv2
from detection_integration import DetectionIntegrator

# Add YOLOv5 to path
YOLO_PATH = Path("yolov5-fire-detection/yolov5")
if str(YOLO_PATH) not in sys.path:
    sys.path.append(str(YOLO_PATH))

from models.common import DetectMultiBackend
from utils.general import check_img_size, non_max_suppression, scale_coords
from utils.torch_utils import select_device
from utils.plots import Annotator, colors
from utils.dataloaders import LoadImages, LoadStreams

class FireDetectionWrapper:
    def __init__(self, weights_path='yolov5-fire-detection/models/FinalFireSmoke/weights/best.pt', sector="default", device='', conf_thres=0.60):
        """
        Initialize the fire detection wrapper
        
        Args:
            weights_path: Path to the YOLOv5 weights file
            sector: The sector/area being monitored
            device: Device to run inference on ('cpu' or cuda device)
            conf_thres: Confidence threshold for detections (increased to 0.60)
        """
        self.device = select_device(device)
        self.model = DetectMultiBackend(weights_path, device=self.device)
        self.stride = self.model.stride
        self.names = self.model.names
        self.pt = self.model.pt
        self.imgsz = check_img_size((640, 640), s=self.stride)
        
        # Initialize incident integrator
        self.integrator = DetectionIntegrator(sector=sector)
        self.conf_thres = conf_thres
        self.iou_thres = 0.45
        self.last_alert_time = {}  # To prevent alert spam
        
    def process_video(self, source_path, show_video=False, save_video=False):
        """
        Process a video file or stream for fire detection
        
        Args:
            source_path: Path to video file or stream URL
            show_video: Whether to show video output
            save_video: Whether to save the output video
        """
        dataset = LoadImages(source_path, img_size=self.imgsz, stride=self.stride, auto=self.pt)
        
        # Video writer setup
        vid_writer = None
        if save_video:
            output_path = f"output_{Path(source_path).stem}.mp4"
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
                    
                    # Get highest confidence fire detection
                    fire_dets = det[det[:, -1] == 0]  # Assuming fire is class 0
                    if len(fire_dets):
                        max_conf_det = fire_dets[fire_dets[:, 4].argmax()]
                        conf = float(max_conf_det[4])
                        
                        # Log incident if confidence is high enough
                        if conf >= self.conf_thres:
                            self.integrator.log_fire_detection(
                                confidence=conf,
                                frame=im0,
                                video_path=source_path
                            )
                    
                    # Draw boxes
                    for *xyxy, conf, cls in reversed(det):
                        c = int(cls)
                        label = f'{self.names[c]} {conf:.2f}'
                        annotator.box_label(xyxy, label, color=colors(c, True))
                
                # Show/save results
                if show_video:
                    cv2.imshow('Fire Detection', im0)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                
                if save_video and vid_writer is not None:
                    vid_writer.write(im0)
        
        # Cleanup
        if save_video and vid_writer is not None:
            vid_writer.release()
        cv2.destroyAllWindows()
    
    def process_stream(self, source='0'):
        """
        Process a live video stream (webcam or IP camera)
        
        Args:
            source: Stream source (0 for webcam, or IP camera URL)
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
                    
                    # Get highest confidence fire detection
                    fire_dets = det[det[:, -1] == 0]  # Assuming fire is class 0
                    if len(fire_dets):
                        max_conf_det = fire_dets[fire_dets[:, 4].argmax()]
                        conf = float(max_conf_det[4])
                        
                        # Log incident if confidence is high enough
                        if conf >= self.conf_thres:
                            self.integrator.log_fire_detection(
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