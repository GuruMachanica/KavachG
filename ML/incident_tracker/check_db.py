from db_handler import SafetyDB
from datetime import datetime, timedelta

def main():
    current_time = datetime.now()
    print(f"\nCurrent time: {current_time}")
    
    db = SafetyDB()
    
    # Get very recent incidents (last 5 minutes)
    end_date = current_time
    start_date = end_date - timedelta(minutes=5)
    
    # Check fire area incidents
    fire_incidents = db.get_incidents_by_sector('test-area-fire', start_date=start_date, end_date=end_date)
    print(f"\nFire incidents in last 5 minutes: {len(fire_incidents)}")
    
    if fire_incidents:
        print("\nMost recent fire incidents:")
        for incident in fire_incidents[:5]:  # Show last 5 incidents
            print(f"Time: {incident['timestamp']}")
            print(f"Type: {incident['incident_type']}")
            print(f"Confidence: {incident['confidence_score']}")
            print(f"Severity: {incident['severity']}")
            print("-" * 30)
    
    # Check fall area incidents
    fall_incidents = db.get_incidents_by_sector('test-area-fall', start_date=start_date, end_date=end_date)
    print(f"\nFall incidents in last 5 minutes: {len(fall_incidents)}")
    
    if fall_incidents:
        print("\nMost recent fall incidents:")
        for incident in fall_incidents[:5]:  # Show last 5 incidents
            print(f"Time: {incident['timestamp']}")
            print(f"Type: {incident['incident_type']}")
            print(f"Confidence: {incident['confidence_score']}")
            print(f"Severity: {incident['severity']}")
            print("-" * 30)

if __name__ == "__main__":
    main() 