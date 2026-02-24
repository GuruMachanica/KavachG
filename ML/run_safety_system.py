import argparse
import logging
from incident_tracker.safety_system import SafetySystem

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/safety_system.log'),
            logging.StreamHandler()
        ]
    )

def main():
    parser = argparse.ArgumentParser(description='Run the Safety Monitoring System')
    parser.add_argument('--source', required=True, help='Path to video file or camera index')
    parser.add_argument('--show', action='store_true', help='Show video output')
    parser.add_argument('--sector', default='main', help='Sector name for incident tracking')
    parser.add_argument('--mongodb-uri', default='mongodb://localhost:27017/', help='MongoDB URI')
    args = parser.parse_args()

    setup_logging()
    logging.info(f"Starting Safety System for sector: {args.sector}")
    
    try:
        # Initialize the safety system
        system = SafetySystem(
            sector=args.sector,
            mongodb_uri=args.mongodb_uri
        )
        
        # Process video
        system.process_video(args.source, show_output=args.show)
        
    except Exception as e:
        logging.error(f"Error running safety system: {str(e)}")
        raise

if __name__ == "__main__":
    main() 