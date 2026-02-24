from fire_detection_wrapper import FireDetectionWrapper
from fall_detection_wrapper import FallDetectionWrapper
from ppe_detection_wrapper import PPEDetectionWrapper
from db_handler import SafetyDB
import argparse
from datetime import datetime, timedelta

def main():
    parser = argparse.ArgumentParser(description='Run safety detection systems')
    parser.add_argument('--mode', choices=['video', 'stream'], required=True,
                       help='Process a video file or live stream')
    parser.add_argument('--source', required=True,
                       help='Path to video file or camera index/URL')
    parser.add_argument('--sector', default='default',
                       help='Sector/area being monitored')
    parser.add_argument('--show-video', action='store_true',
                       help='Show video output')
    parser.add_argument('--save-video', action='store_true',
                       help='Save annotated video output')
    parser.add_argument('--fire-weights',
                       default='yolov5-fire-detection/models/FinalFireSmoke/weights/best.pt',
                       help='Path to fire detection weights')
    parser.add_argument('--fall-weights',
                       default='Image-based-Human-Fall-Detection/best.pt',
                       help='Path to fall detection weights')
    parser.add_argument('--ppe-weights',
                       default='Construction-Site-Safety-PPE-Detection/models/best.pt',
                       help='Path to PPE detection weights')
    
    args = parser.parse_args()
    
    # Initialize detection systems
    fire_detector = FireDetectionWrapper(
        weights_path=args.fire_weights,
        sector=args.sector
    )
    
    fall_detector = FallDetectionWrapper(
        weights_path=args.fall_weights,
        sector=args.sector
    )
    
    ppe_detector = PPEDetectionWrapper(
        weights_path=args.ppe_weights,
        sector=args.sector
    )
    
    # Process video/stream based on mode
    if args.mode == 'video':
        # Process with each detector
        print("Running fire detection...")
        fire_detector.process_video(
            args.source,
            show_video=args.show_video,
            save_video=args.save_video
        )
        
        print("Running fall detection...")
        fall_detector.process_video(
            args.source,
            output_path='output_fall.mp4' if args.save_video else None,
            show_video=args.show_video
        )
        
        print("Running PPE detection...")
        ppe_detector.process_video(
            args.source,
            show_video=args.show_video,
            save_video=args.save_video
        )
    else:  # stream mode
        print("Processing live stream...")
        try:
            # Note: In stream mode, we process with one detector at a time
            # You might want to implement multi-threading for parallel processing
            print("Running fire detection (press 'q' to switch to fall detection)...")
            fire_detector.process_stream(args.source)
            
            print("Running fall detection (press 'q' to switch to PPE detection)...")
            fall_detector.process_stream(args.source)
            
            print("Running PPE detection (press 'q' to exit)...")
            ppe_detector.process_stream(args.source)
        except KeyboardInterrupt:
            print("\nStopped by user")
    
    # Print incident summary
    db = SafetyDB()
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=1)  # Last hour's incidents
    
    stats = db.get_incident_stats(start_time, end_time)
    print("\nIncident Summary (Last Hour):")
    print("-" * 50)
    
    for incident_type, data in stats.items():
        print(f"\n{incident_type}:")
        print(f"Total incidents: {data['total']}")
        print("By severity:")
        for severity, count in data['by_severity'].items():
            print(f"  {severity}: {count}")
    
    print("\nUnaddressed Incidents:")
    print("-" * 50)
    unaddressed = db.get_unaddressed_incidents()
    for incident in unaddressed:
        print(f"Type: {incident['incident_type']}")
        print(f"Time: {incident['timestamp']}")
        print(f"Sector: {incident['sector']}")
        print(f"Severity: {incident['severity']}")
        print(f"Description: {incident['description']}")
        print("-" * 30)

if __name__ == "__main__":
    main() 