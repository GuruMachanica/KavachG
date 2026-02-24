import os
import sys
import subprocess
import shutil
from pathlib import Path
import logging

def setup_logging():
    """Configure logging"""
    os.makedirs('logs', exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/setup.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        raise SystemError("Python 3.8 or higher is required")
    logging.info(f"Python version check passed: {sys.version}")

def setup_directories():
    """Create necessary directories"""
    directories = [
        'logs',
        'detections',
        'detections/fire',
        'detections/fall',
        'models'
    ]
    for dir_path in directories:
        os.makedirs(dir_path, exist_ok=True)
        logging.info(f"Created directory: {dir_path}")

def install_requirements():
    """Install required Python packages"""
    requirements = [
        'torch>=1.7.0',
        'torchvision>=0.8.1',
        'opencv-python>=4.5.0',
        'pymongo>=3.11.0',
        'numpy>=1.19.0',
        'pydantic>=1.8.0',
        'python-dotenv>=0.19.0'
    ]
    
    logging.info("Installing Python requirements...")
    for req in requirements:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", req])
            logging.info(f"Installed {req}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to install {req}: {str(e)}")
            raise

def setup_yolo_models():
    """Clone and setup YOLO models"""
    repos = {
        'fire': {
            'url': 'https://github.com/robmarkcole/fire-detection-from-images',
            'dir': 'yolov5-fire-detection',
            'weights_url': 'https://github.com/robmarkcole/fire-detection-from-images/releases/download/v1.0/best.pt',
            'weights_path': 'models/FinalFireSmoke/weights/best.pt'
        },
        'fall': {
            'url': 'https://github.com/RizwanMunawar/yolov7-pose-estimation',
            'dir': 'Image-based-Human-Fall-Detection',
            'weights_url': 'https://github.com/RizwanMunawar/yolov7-pose-estimation/releases/download/v1.0/yolov7-w6-pose.pt',
            'weights_path': 'best.pt'
        }
    }
    
    for model_type, repo_info in repos.items():
        try:
            # Clone repository if not exists
            if not os.path.exists(repo_info['dir']):
                subprocess.check_call(['git', 'clone', repo_info['url'], repo_info['dir']])
                logging.info(f"Cloned {model_type} detection repository")
            
            # Download weights
            weights_dir = os.path.join(repo_info['dir'], os.path.dirname(repo_info['weights_path']))
            os.makedirs(weights_dir, exist_ok=True)
            weights_path = os.path.join(repo_info['dir'], repo_info['weights_path'])
            
            if not os.path.exists(weights_path):
                subprocess.check_call(['wget', repo_info['weights_url'], '-O', weights_path])
                logging.info(f"Downloaded {model_type} detection weights")
            
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to setup {model_type} detection: {str(e)}")
            raise

def create_env_file():
    """Create .env file with default configuration"""
    env_content = """
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/
DB_NAME=safety_monitoring
COLLECTION_NAME=incidents

# Model Paths
FIRE_WEIGHTS=yolov5-fire-detection/models/FinalFireSmoke/weights/best.pt
FALL_WEIGHTS=Image-based-Human-Fall-Detection/best.pt

# Detection Settings
CONFIDENCE_THRESHOLD=0.6
DEVICE=cpu  # or cuda:0 for GPU
"""
    
    with open('.env', 'w') as f:
        f.write(env_content.strip())
    logging.info("Created .env configuration file")

def verify_setup():
    """Verify all components are properly setup"""
    checks = [
        ('Python Packages', lambda: subprocess.check_call([sys.executable, "-m", "pip", "freeze"], 
                                                        stdout=subprocess.DEVNULL)),
        ('Fire Detection Model', lambda: os.path.exists('yolov5-fire-detection/models/FinalFireSmoke/weights/best.pt')),
        ('Fall Detection Model', lambda: os.path.exists('Image-based-Human-Fall-Detection/best.pt')),
        ('Directories', lambda: all(os.path.exists(d) for d in ['logs', 'detections'])),
        ('Environment File', lambda: os.path.exists('.env'))
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        try:
            check_func()
            logging.info(f"✓ {check_name} check passed")
        except Exception as e:
            all_passed = False
            logging.error(f"✗ {check_name} check failed: {str(e)}")
    
    return all_passed

def main():
    """Main setup function"""
    setup_logging()
    logging.info("Starting setup process...")
    
    try:
        check_python_version()
        setup_directories()
        install_requirements()
        setup_yolo_models()
        create_env_file()
        
        if verify_setup():
            logging.info("Setup completed successfully!")
            print("\nSetup completed successfully! You can now run the system using:")
            print("python incident_tracker/run_safety_system.py --source <video_source> --show")
        else:
            logging.error("Setup completed with errors. Please check the logs.")
            sys.exit(1)
            
    except Exception as e:
        logging.error(f"Setup failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 