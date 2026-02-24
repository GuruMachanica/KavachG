import argparse
import subprocess
import time
import os
import sys

def setup_directories():
    """Ensure all necessary directories exist"""
    os.makedirs("detections/fire", exist_ok=True)
    os.makedirs("detections/fall", exist_ok=True)
    os.makedirs("detections/ppe", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

def run_fire_detection(video_source):
    """Run fire detection model on the specified video"""
    print("\n===== RUNNING FIRE DETECTION =====")
    fire_cmd = [
        "python", 
        "yolov5-fire-detection/detect.py", 
        "--weights", "yolov5-fire-detection/models/FinalFireSmoke/weights/best.pt",
        "--img", "640",
        "--conf", "0.25",
        "--source", video_source,
        "--save-txt"
    ]
    
    subprocess.run(fire_cmd)
    print("Fire detection completed!")

def run_fall_detection(video_source):
    """Run fall detection model on the specified video"""
    print("\n===== RUNNING FALL DETECTION =====")
    # Save current directory
    current_dir = os.getcwd()
    
    # Change to fall detection directory
    os.chdir("Image-based-Human-Fall-Detection")
    
    # Run fall detection
    fall_cmd = [
        "python",
        "detect_video.py",
        "--source", f"../{video_source}"
    ]
    
    subprocess.run(fall_cmd)
    
    # Return to original directory
    os.chdir(current_dir)
    print("Fall detection completed!")

def run_ppe_detection(video_source):
    """Run PPE detection model on the specified video"""
    print("\n===== RUNNING PPE DETECTION =====")
    # Construct the working directory path
    ppe_dir = os.path.join(os.getcwd(), "Construction-Site-Safety-PPE-Detection")
    
    # Check if the model exists
    model_path = os.path.join(ppe_dir, "models", "best.pt")
    if not os.path.exists(model_path):
        model_path = "models/best.pt"  # fallback to models directory
    
    ppe_cmd = [
        "python",
        "Construction-Site-Safety-PPE-Detection/detect.py",
        "--weights", model_path,
        "--img", "640",
        "--conf", "0.25",
        "--source", video_source
    ]
    
    subprocess.run(ppe_cmd)
    print("PPE detection completed!")

def main():
    parser = argparse.ArgumentParser(description="Run enhanced safety system with multiple detection types")
    parser.add_argument("--source", required=True, help="Path to video file")
    parser.add_argument("--fire", action="store_true", help="Run fire detection")
    parser.add_argument("--fall", action="store_true", help="Run fall detection")
    parser.add_argument("--ppe", action="store_true", help="Run PPE detection")
    parser.add_argument("--all", action="store_true", help="Run all detection types")
    
    args = parser.parse_args()
    
    # Setup directories
    setup_directories()
    
    # Validate source file
    if not os.path.exists(args.source):
        print(f"Error: Source file '{args.source}' does not exist.")
        return
    
    # Run requested detections
    if args.all or args.fire:
        run_fire_detection(args.source)
    
    if args.all or args.fall:
        run_fall_detection(args.source)
    
    if args.all or args.ppe:
        run_ppe_detection(args.source)
    
    print("\nAll requested detection tasks completed!")

if __name__ == "__main__":
    main() 