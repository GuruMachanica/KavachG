# Safety Incident Tracking System

This system integrates with the fire detection, fall detection, and PPE violation detection models to track and manage safety incidents in a MongoDB database.

## Features

- Automatic incident logging for:
  - Fire detection
  - Fall detection
  - PPE violations
- Severity classification based on detection confidence
- Incident management with supervisor acknowledgment
- Incident statistics and reporting
- Image and video evidence storage
- Sector-based incident tracking

## Setup

1. Install MongoDB on your system if not already installed
   - Download from: https://www.mongodb.com/try/download/community
   - Follow installation instructions for your OS

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with the following content:
   ```
   MONGODB_URI=mongodb://localhost:27017/
   DB_NAME=safety_monitoring
   COLLECTION_NAME=incidents
   ```

4. Create the detections directory:
   ```bash
   mkdir detections
   ```

## Integration with Detection Models

### Fire Detection Integration
```python
from detection_integration import DetectionIntegrator

# Initialize the integrator with the sector name
integrator = DetectionIntegrator(sector="Building A")

# When fire is detected
incident_id = integrator.log_fire_detection(
    confidence=0.95,  # Detection confidence
    frame=detected_frame,  # Optional: numpy array of the frame
    video_path="path/to/video.mp4"  # Optional: path to the source video
)
```

### Fall Detection Integration
```python
# When fall is detected
incident_id = integrator.log_fall_detection(
    confidence=0.88,
    frame=detected_frame,
    video_path="path/to/video.mp4"
)
```

### PPE Violation Integration
```python
# When PPE violation is detected
incident_id = integrator.log_ppe_violation(
    missing_items=["Hardhat", "Safety Vest"],
    confidence=0.92,
    frame=detected_frame,
    video_path="path/to/video.mp4"
)
```

## Supervisor Interface

### Marking Incidents as Addressed
```python
from db_handler import SafetyDB

db = SafetyDB()

# Mark an incident as addressed
db.mark_addressed(
    incident_id="incident_id_here",
    supervisor="John Doe",
    notes="Issue resolved - Worker provided with proper PPE"
)
```

### Viewing Incidents
```python
# Get all unaddressed incidents
unaddressed = db.get_unaddressed_incidents()

# Get incidents by sector
sector_incidents = db.get_incidents_by_sector("Building A")

# Get incident statistics
stats = db.get_incident_stats()
```

## Severity Levels

The system automatically determines severity based on detection confidence:

### Fire Detection
- CRITICAL: confidence > 90%
- HIGH: confidence > 70%
- MEDIUM: confidence > 50%
- LOW: confidence ≤ 50%

### Fall Detection
- HIGH: confidence > 85%
- MEDIUM: confidence > 60%
- LOW: confidence ≤ 60%

### PPE Violations
- HIGH: confidence > 95%
- MEDIUM: confidence > 75%
- LOW: confidence ≤ 75% 