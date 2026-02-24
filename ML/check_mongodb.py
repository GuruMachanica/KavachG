import pymongo
from pymongo import MongoClient
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_mongodb_connection():
    """Check MongoDB connection and setup initial database structure"""
    try:
        # Try to connect to MongoDB
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        
        # Check if the connection is successful
        client.server_info()
        logger.info("Successfully connected to MongoDB")
        
        # Create database and collection
        db = client.safety_monitoring
        collection = db.incidents
        
        # Create indexes
        collection.create_index([("timestamp", -1)])
        collection.create_index([("incident_type", 1)])
        collection.create_index([("sector", 1)])
        
        logger.info("Database and collections setup completed")
        return True
        
    except pymongo.errors.ServerSelectionTimeoutError:
        logger.error("Could not connect to MongoDB. Please make sure MongoDB is running")
        return False
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return False

if __name__ == "__main__":
    if not check_mongodb_connection():
        sys.exit(1)
    logger.info("MongoDB check completed successfully") 