from pymongo import MongoClient
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
import os
from enum import Enum
import logging

# Configure logging
logging.basicConfig(
    filename='safety_db.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class IncidentType(str, Enum):
    FIRE = "fire"
    FALL = "fall"
    PPE_VIOLATION = "ppe_violation"

class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Incident(BaseModel):
    incident_type: IncidentType
    timestamp: datetime
    sector: str
    severity: Severity
    description: str
    image_path: Optional[str] = None
    video_path: Optional[str] = None
    addressed: bool = False
    addressed_by: Optional[str] = None
    addressed_at: Optional[datetime] = None
    confidence_score: float
    notes: Optional[str] = None

class SafetyDB:
    def __init__(self, mongodb_uri: str = "mongodb://localhost:27017/",
                 db_name: str = "safety_monitoring",
                 collection_name: str = "incidents"):
        try:
            self.client = MongoClient(mongodb_uri)
            self.db = self.client[db_name]
            self.collection = self.db[collection_name]
            
            # Create indexes
            self.collection.create_index([("timestamp", -1)])
            self.collection.create_index([("incident_type", 1)])
            self.collection.create_index([("addressed", 1)])
            self.collection.create_index([("sector", 1)])
            
            logging.info(f"Successfully connected to MongoDB: {db_name}.{collection_name}")
        except Exception as e:
            logging.error(f"Failed to initialize MongoDB connection: {str(e)}")
            raise

    def log_incident(self, incident: Incident) -> str:
        """Log a new incident to the database"""
        try:
            incident_dict = incident.dict()
            result = self.collection.insert_one(incident_dict)
            incident_id = str(result.inserted_id)
            logging.info(f"Successfully logged incident: {incident_id} - Type: {incident.incident_type}, Sector: {incident.sector}")
            return incident_id
        except Exception as e:
            logging.error(f"Failed to log incident: {str(e)}")
            raise

    def mark_addressed(self, incident_id: str, supervisor: str, notes: Optional[str] = None) -> bool:
        """Mark an incident as addressed by a supervisor"""
        try:
            result = self.collection.update_one(
                {"_id": incident_id},
                {
                    "$set": {
                        "addressed": True,
                        "addressed_by": supervisor,
                        "addressed_at": datetime.now(),
                        "notes": notes
                    }
                }
            )
            success = result.modified_count > 0
            if success:
                logging.info(f"Incident {incident_id} marked as addressed by {supervisor}")
            else:
                logging.warning(f"Failed to mark incident {incident_id} as addressed - incident not found")
            return success
        except Exception as e:
            logging.error(f"Error marking incident {incident_id} as addressed: {str(e)}")
            raise

    def get_unaddressed_incidents(self, incident_type: Optional[IncidentType] = None) -> List[dict]:
        """Get all unaddressed incidents, optionally filtered by type"""
        try:
            query = {"addressed": False}
            if incident_type:
                query["incident_type"] = incident_type
            results = list(self.collection.find(query).sort("timestamp", -1))
            logging.info(f"Retrieved {len(results)} unaddressed incidents" + 
                        (f" of type {incident_type}" if incident_type else ""))
            return results
        except Exception as e:
            logging.error(f"Error retrieving unaddressed incidents: {str(e)}")
            raise

    def get_incidents_by_sector(self, sector: str, start_date: Optional[datetime] = None,
                              end_date: Optional[datetime] = None) -> List[dict]:
        """Get incidents for a specific sector with optional date range"""
        try:
            query = {"sector": sector}
            if start_date or end_date:
                query["timestamp"] = {}
                if start_date:
                    query["timestamp"]["$gte"] = start_date
                if end_date:
                    query["timestamp"]["$lte"] = end_date
            results = list(self.collection.find(query).sort("timestamp", -1))
            logging.info(f"Retrieved {len(results)} incidents for sector {sector}" +
                        (f" from {start_date}" if start_date else "") +
                        (f" to {end_date}" if end_date else ""))
            return results
        except Exception as e:
            logging.error(f"Error retrieving incidents for sector {sector}: {str(e)}")
            raise

    def get_incident_stats(self, start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None) -> dict:
        """Get statistics about incidents"""
        try:
            match_stage = {}
            if start_date or end_date:
                match_stage["timestamp"] = {}
                if start_date:
                    match_stage["timestamp"]["$gte"] = start_date
                if end_date:
                    match_stage["timestamp"]["$lte"] = end_date

            pipeline = [
                {"$match": match_stage},
                {"$group": {
                    "_id": {
                        "type": "$incident_type",
                        "severity": "$severity"
                    },
                    "count": {"$sum": 1}
                }},
                {"$group": {
                    "_id": "$_id.type",
                    "by_severity": {
                        "$push": {
                            "severity": "$_id.severity",
                            "count": "$count"
                        }
                    },
                    "total": {"$sum": "$count"}
                }}
            ]
            
            results = {item["_id"]: {
                "total": item["total"],
                "by_severity": {x["severity"]: x["count"] for x in item["by_severity"]}
            } for item in self.collection.aggregate(pipeline)}
            
            logging.info(f"Generated incident statistics" +
                        (f" from {start_date}" if start_date else "") +
                        (f" to {end_date}" if end_date else ""))
            return results
        except Exception as e:
            logging.error(f"Error generating incident statistics: {str(e)}")
            raise

    def __del__(self):
        try:
            self.client.close()
            logging.info("MongoDB connection closed")
        except:
            pass 