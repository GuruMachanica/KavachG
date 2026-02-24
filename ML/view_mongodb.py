from pymongo import MongoClient
from datetime import datetime, timedelta
import argparse
from tabulate import tabulate
import pandas as pd

def get_stats(incidents):
    """Get statistics from incidents"""
    stats = {
        'fire': {'low': 0, 'medium': 0, 'high': 0, 'critical': 0},
        'fall': {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
    }
    
    for inc in incidents:
        inc_type = inc['incident_type']
        severity = inc['severity']
        stats[inc_type][severity] += 1
    
    return stats

def main():
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client.safety_monitoring
    
    # Get all incidents
    incidents = list(db.incidents.find().sort('timestamp', -1))
    
    if not incidents:
        print("No incidents found in database!")
        return
        
    # Basic stats
    print("\n=== Database Statistics ===")
    print(f"Total incidents: {len(incidents)}")
    print(f"First incident: {incidents[-1]['timestamp']}")
    print(f"Latest incident: {incidents[0]['timestamp']}")
    
    # Get statistics
    stats = get_stats(incidents)
    
    # Create summary tables
    fire_data = [[sev, count] for sev, count in stats['fire'].items()]
    fall_data = [[sev, count] for sev, count in stats['fall'].items()]
    
    print("\n=== Fire Incidents by Severity ===")
    print(tabulate(fire_data, headers=['Severity', 'Count'], tablefmt='grid'))
    print(f"Total Fire Incidents: {sum(stats['fire'].values())}")
    
    print("\n=== Fall Incidents by Severity ===")
    print(tabulate(fall_data, headers=['Severity', 'Count'], tablefmt='grid'))
    print(f"Total Fall Incidents: {sum(stats['fall'].values())}")
    
    # Show latest incidents
    print("\n=== Latest 5 Incidents ===")
    latest = incidents[:5]
    latest_data = []
    for inc in latest:
        latest_data.append([
            inc['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
            inc['incident_type'],
            inc['severity'],
            f"{inc['confidence_score']:.2f}",
            inc['sector']
        ])
    
    print(tabulate(latest_data, 
                  headers=['Timestamp', 'Type', 'Severity', 'Confidence', 'Sector'],
                  tablefmt='grid'))
    
    # Confidence score distribution
    print("\n=== Confidence Score Distribution ===")
    fire_conf = [inc['confidence_score'] for inc in incidents if inc['incident_type'] == 'fire']
    fall_conf = [inc['confidence_score'] for inc in incidents if inc['incident_type'] == 'fall']
    
    if fire_conf:
        print(f"Fire Detection:")
        print(f"  Min: {min(fire_conf):.2f}")
        print(f"  Max: {max(fire_conf):.2f}")
        print(f"  Avg: {sum(fire_conf)/len(fire_conf):.2f}")
    
    if fall_conf:
        print(f"\nFall Detection:")
        print(f"  Min: {min(fall_conf):.2f}")
        print(f"  Max: {max(fall_conf):.2f}")
        print(f"  Avg: {sum(fall_conf)/len(fall_conf):.2f}")
    
    # Time-based analysis
    print("\n=== Incident Timeline ===")
    last_24h = len([i for i in incidents if i['timestamp'] > datetime.now() - timedelta(hours=24)])
    last_1h = len([i for i in incidents if i['timestamp'] > datetime.now() - timedelta(hours=1)])
    
    print(f"Last hour: {last_1h} incidents")
    print(f"Last 24 hours: {last_24h} incidents")
    
if __name__ == '__main__':
    main() 