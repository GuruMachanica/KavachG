from pymongo import MongoClient
from datetime import datetime, timedelta
import argparse

def format_incident(incident):
    return f"""
Incident ID: {incident['_id']}
Type: {incident['incident_type']}
Timestamp: {incident['timestamp']}
Sector: {incident['sector']}
Severity: {incident['severity']}
Confidence: {incident['confidence_score']:.2f}
Image Path: {incident['image_path']}
Description: {incident['description']}
{'Addressed by: ' + incident['addressed_by'] if incident.get('addressed_by') else 'Not addressed'}
---"""

def main():
    parser = argparse.ArgumentParser(description='View safety incidents from MongoDB')
    parser.add_argument('--type', choices=['fire', 'fall', 'all'], default='all',
                       help='Type of incidents to view')
    parser.add_argument('--last', type=int, default=5,
                       help='Number of most recent incidents to show')
    parser.add_argument('--sector', type=str, help='Filter by sector')
    parser.add_argument('--severity', choices=['low', 'medium', 'high', 'critical'],
                       help='Filter by severity')
    parser.add_argument('--hours', type=int, help='Show incidents from last N hours')
    
    args = parser.parse_args()
    
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client.safety_monitoring
    
    # Build query
    query = {}
    if args.type != 'all':
        query['incident_type'] = args.type
    if args.sector:
        query['sector'] = args.sector
    if args.severity:
        query['severity'] = args.severity
    if args.hours:
        time_threshold = datetime.now() - timedelta(hours=args.hours)
        query['timestamp'] = {'$gte': time_threshold}
    
    # Get incidents
    incidents = list(db.incidents.find(query).sort('timestamp', -1).limit(args.last))
    
    # Print results
    print(f"\nFound {len(incidents)} incidents matching criteria:")
    for incident in incidents:
        print(format_incident(incident))
    
    # Print summary
    print(f"\nSummary:")
    print(f"Total incidents in database: {db.incidents.count_documents({})}")
    if args.type != 'all':
        print(f"Total {args.type} incidents: {db.incidents.count_documents({'incident_type': args.type})}")
    
if __name__ == '__main__':
    main() 