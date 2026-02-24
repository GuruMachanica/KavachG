from safety_system import SafetySystem
import argparse
import sys
import logging
import os

def setup_logging():
    """Setup logging configuration"""
    os.makedirs('logs', exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/run_safety.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def verify_paths(args):
    """Verify that all required paths exist"""
    if not args.source.isdigit() and not os.path.exists(args.source):
        raise FileNotFoundError(f"Video source not found: {args.source}")
    
    if args.fire_weights and not os.path.exists(args.fire_weights):
        raise FileNotFoundError(f"Fire detection weights not found: {args.fire_weights}")
    
    if args.fall_weights and not os.path.exists(args.fall_weights):
        raise FileNotFoundError(f"Fall detection weights not found: {args.fall_weights}")

def main():
    parser = argparse.ArgumentParser(description='Run unified safety monitoring system')
    
    # Required arguments
    parser.add_argument('--source', required=True,
                       help='Path to video file or camera index (0 for webcam)')
    
    # Optional arguments
    parser.add_argument('--sector', default='default',
                       help='Sector/area being monitored')
    parser.add_argument('--show', action='store_true',
                       help='Show detection output')
    parser.add_argument('--device', default='',
                       help='cuda device (e.g. 0 or 0,1,2,3) or cpu')
    parser.add_argument('--fire-weights',
                       default='yolov5-fire-detection/models/FinalFireSmoke/weights/best.pt',
                       help='Path to fire detection weights')
    parser.add_argument('--fall-weights',
                       default='Image-based-Human-Fall-Detection/best.pt',
                       help='Path to fall detection weights')
    parser.add_argument('--mongodb-uri',
                       default='mongodb://localhost:27017/',
                       help='MongoDB connection URI')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging()
    logging.info("Starting safety monitoring system")
    
    try:
        # Verify paths
        verify_paths(args)
        
        # Initialize safety system
        logging.info(f"Initializing system for sector: {args.sector}")
        system = SafetySystem(
            sector=args.sector,
            mongodb_uri=args.mongodb_uri,
            fire_weights=args.fire_weights,
            fall_weights=args.fall_weights,
            device=args.device
        )
        
        # Process video
        logging.info(f"Processing video from source: {args.source}")
        print(f"\nMonitoring sector: {args.sector}")
        print("Press 'q' to quit\n")
        
        system.process_video(args.source, show_output=args.show)
        
        logging.info("Processing completed successfully")
        
    except KeyboardInterrupt:
        logging.info("Stopped by user")
        print("\nStopped by user")
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        print(f"\nError: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 