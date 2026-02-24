import argparse
import os
import sys
import subprocess
import time
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/all_models.log'),
        logging.StreamHandler()
    ]
)

def ensure_directories():
    """Ensure all necessary directories exist"""
    os.makedirs("logs", exist_ok=True)
    os.makedirs("detections/fire", exist_ok=True)
    os.makedirs("detections/fall", exist_ok=True)
    os.makedirs("detections/ppe", exist_ok=True)

def get_absolute_path(relative_path):
    """Convert relative path to absolute path"""
    current_dir = os.getcwd()
    return os.path.join(current_dir, relative_path)

def run_fire_detection(video_path, show_output=True, save_output=True):
    """Run fire detection model on the video"""
    print("\n===== RUNNING FIRE DETECTION =====")
    logging.info("Starting fire detection")
    
    # Ensure yolov5 directory is in path
    sys.path.append(get_absolute_path("yolov5-fire-detection/yolov5"))
    
    weights_path = get_absolute_path("yolov5-fire-detection/models/FinalFireSmoke/weights/best.pt")
    
    # Build command
    cmd = [
        "python",
        get_absolute_path("yolov5-fire-detection/yolov5/detect.py"),
        "--weights", weights_path,
        "--img", "640",
        "--conf", "0.25",
        "--source", video_path
    ]
    
    if save_output:
        cmd.extend(["--save-txt", "--save-conf"])
    
    # Run the command
    try:
        subprocess.run(cmd, check=True)
        print("Fire detection completed successfully")
        logging.info("Fire detection completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running fire detection: {e}")
        logging.error(f"Error running fire detection: {e}")
        return False

def run_fall_detection(video_path, show_output=True, save_output=True):
    """Run fall detection model on the video"""
    print("\n===== RUNNING FALL DETECTION =====")
    logging.info("Starting fall detection")
    
    # Save current directory
    current_dir = os.getcwd()
    
    try:
        # Change to fall detection directory
        fall_dir = get_absolute_path("Image-based-Human-Fall-Detection")
        os.chdir(fall_dir)
        
        # Build command
        cmd = [
            "python",
            "detect_video.py",
            "--source", video_path
        ]
        
        if os.path.isabs(video_path):
            # If absolute path, use it directly
            cmd = [
                "python",
                "detect_video.py",
                "--source", video_path
            ]
        else:
            # If relative, make it relative to original directory
            abs_video_path = os.path.join(current_dir, video_path)
            cmd = [
                "python",
                "detect_video.py",
                "--source", abs_video_path
            ]
        
        # Run the command
        subprocess.run(cmd, check=True)
        print("Fall detection completed successfully")
        logging.info("Fall detection completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running fall detection: {e}")
        logging.error(f"Error running fall detection: {e}")
        return False
    finally:
        # Restore original directory
        os.chdir(current_dir)

def run_ppe_detection(video_path, show_output=True, save_output=True):
    """Run PPE detection model on the video"""
    print("\n===== RUNNING PPE DETECTION =====")
    logging.info("Starting PPE detection")
    
    # Save current directory
    current_dir = os.getcwd()
    
    try:
        # Change to PPE detection directory
        ppe_dir = get_absolute_path("Construction-Site-Safety-PPE-Detection")
        model_path = os.path.join(ppe_dir, "models", "best.pt")
        
        if not os.path.exists(ppe_dir):
            print(f"PPE detection directory not found: {ppe_dir}")
            logging.error(f"PPE detection directory not found: {ppe_dir}")
            return False
            
        os.chdir(ppe_dir)
        
        if os.path.isabs(video_path):
            # If absolute path, use it directly
            source_path = video_path
        else:
            # If relative, make it relative to original directory
            source_path = os.path.join(current_dir, video_path)
        
        # Build command - check if detect.py exists
        detect_script = "detect.py"
        if not os.path.exists(detect_script):
            # Look for alternatives
            if os.path.exists("yolov5/detect.py"):
                detect_script = "yolov5/detect.py"
            elif os.path.exists("predict.py"):
                detect_script = "predict.py"
            else:
                print("Could not find detection script in PPE directory")
                logging.error("Could not find detection script in PPE directory")
                return False
        
        cmd = [
            "python",
            detect_script,
            "--weights", "models/best.pt",
            "--img", "640",
            "--conf", "0.25",
            "--source", source_path
        ]
        
        # Run the command
        subprocess.run(cmd, check=True)
        print("PPE detection completed successfully")
        logging.info("PPE detection completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running PPE detection: {e}")
        logging.error(f"Error running PPE detection: {e}")
        return False
    finally:
        # Restore original directory
        os.chdir(current_dir)

def run_safety_system(video_path, sector):
    """Run the standard safety system"""
    print("\n===== RUNNING STANDARD SAFETY SYSTEM =====")
    logging.info(f"Starting standard safety system for sector: {sector}")
    
    # Build command
    cmd = [
        "python",
        "run_safety_system.py",
        "--source", video_path,
        "--show",
        "--sector", sector
    ]
    
    # Run the command
    try:
        subprocess.run(cmd, check=True)
        print("Safety system completed successfully")
        logging.info("Safety system completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running safety system: {e}")
        logging.error(f"Error running safety system: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Run KavachG Safety Detection Models")
    parser.add_argument("--source", required=True, help="Path to video file or camera index")
    parser.add_argument("--mode", choices=["fire", "fall", "ppe", "all", "standard"], default="all", 
                       help="Which detection mode to run")
    parser.add_argument("--sector", default="main", help="Sector name for incident tracking")
    parser.add_argument("--backend", action="store_true", help="Start the backend server")
    parser.add_argument("--frontend", action="store_true", help="Start the frontend server")
    parser.add_argument("--no-show", action="store_true", help="Don't show output video")
    
    args = parser.parse_args()
    
    # Ensure directories exist
    ensure_directories()
    
    # Make sure video path is valid or camera index
    if not args.source.isdigit():  # Not a camera index
        video_path = args.source  # Use relative path
        if not os.path.exists(video_path):
            print(f"Warning: Video file not found: {video_path}")
            logging.warning(f"Video file not found: {video_path}")
    else:
        video_path = args.source  # Camera index
    
    # Start backend if requested
    if args.backend:
        print("\n===== STARTING BACKEND SERVER =====")
        # Navigate to backend directory (2 levels up)
        backend_dir = os.path.abspath(os.path.join(os.getcwd(), "../backend"))
        if os.path.exists(backend_dir):
            backend_process = subprocess.Popen(
                ["npm", "start"],
                cwd=backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print(f"Backend server started at http://localhost:5001")
        else:
            print(f"Backend directory not found: {backend_dir}")
    
    # Start frontend if requested
    if args.frontend:
        print("\n===== STARTING FRONTEND SERVER =====")
        # Navigate to frontend directory (2 levels up)
        frontend_dir = os.path.abspath(os.path.join(os.getcwd(), "../FrontEnd/FrontEnd"))
        if os.path.exists(frontend_dir):
            frontend_process = subprocess.Popen(
                ["npm", "start"],
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print(f"Frontend server started at http://localhost:3000")
        else:
            print(f"Frontend directory not found: {frontend_dir}")
    
    # Run requested detection mode
    show_output = not args.no_show
    
    try:
        if args.mode == "fire" or args.mode == "all":
            run_fire_detection(video_path, show_output)
        
        if args.mode == "fall" or args.mode == "all":
            run_fall_detection(video_path, show_output)
        
        if args.mode == "ppe" or args.mode == "all":
            run_ppe_detection(video_path, show_output)
        
        if args.mode == "standard":
            run_safety_system(video_path, args.sector)
            
    except KeyboardInterrupt:
        print("\nDetection stopped by user")
        logging.info("Detection stopped by user")
    
    print("\nAll processes completed.")

if __name__ == "__main__":
    main() 