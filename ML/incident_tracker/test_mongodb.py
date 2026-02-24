from db_handler import SafetyDB, Incident, IncidentType, Severity
from datetime import datetime

def test_mongodb_connection():
    try:
        # Initialize database
        db = SafetyDB()
        
        # Create a test incident
        test_incident = Incident(
            incident_type=IncidentType.FIRE,
            timestamp=datetime.now(),
            sector="Test Sector",
            severity=Severity.HIGH,
            description="Test incident",
            confidence_score=0.95
        )
        
        # Log the incident
        incident_id = db.log_incident(test_incident)
        print(f"Successfully created test incident with ID: {incident_id}")
        
        # Retrieve unaddressed incidents
        unaddressed = db.get_unaddressed_incidents()
        print(f"\nFound {len(unaddressed)} unaddressed incidents")
        
        # Mark the incident as addressed
        success = db.mark_addressed(incident_id, "Test Supervisor", "Test resolved")
        print(f"Marked incident as addressed: {success}")
        
        # Get statistics
        stats = db.get_incident_stats()
        print("\nIncident statistics:")
        print(stats)
        
        print("\nMongoDB connection and operations are working correctly!")
        return True
        
    except Exception as e:
        print(f"\nError testing MongoDB connection: {str(e)}")
        return False

if __name__ == "__main__":
    test_mongodb_connection() 