import os
import sys
import subprocess
import logging
from pathlib import Path

def setup_logging():
    """Configure logging to both file and stdout"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "setup.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

def install_requirements():
    """Install required packages using pip"""
    try:
        logging.info("Installing required packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        logging.info("Successfully installed required packages")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to install requirements: {e}")
        sys.exit(1)

def setup_directories():
    """Create necessary directories"""
    dirs = ["logs", "detections", "models"]
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
        logging.info(f"Created directory: {dir_name}")

def verify_yolo_paths():
    """Verify YOLO model paths and clone if necessary"""
    yolo_paths = {
        "fire": "yolov5-fire-detection",
        "fall": "Image-based-Human-Fall-Detection",
        "ppe": "Construction-Site-Safety-PPE-Detection"
    }
    
    for model_type, path in yolo_paths.items():
        if not Path(path).exists():
            logging.error(f"{model_type.upper()} detection model path not found: {path}")
            logging.info("Please ensure you have cloned the required model repositories")
            return False
    return True

def main():
    setup_logging()
    logging.info("Starting environment setup...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        logging.error("Python 3.8 or higher is required")
        sys.exit(1)
    
    # Create directories
    setup_directories()
    
    # Install requirements
    install_requirements()
    
    # Verify YOLO paths
    if not verify_yolo_paths():
        logging.error("Please clone the required model repositories before proceeding")
        sys.exit(1)
    
    logging.info("Environment setup completed successfully!")
    logging.info("\nYou can now run the safety system using:")
    logging.info("python incident_tracker/run_safety_system.py --source sample_test/Fire.mp4 --show")

if __name__ == "__main__":
    main() 