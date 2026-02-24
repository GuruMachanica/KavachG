import os
import time
from datetime import datetime, timedelta
import logging
from collections import defaultdict
import json

def analyze_logs(log_file='safety_db.log', time_window_minutes=60):
    """Analyze the database logs for the specified time window"""
    if not os.path.exists(log_file):
        print(f"Log file {log_file} not found")
        return

    current_time = datetime.now()
    cutoff_time = current_time - timedelta(minutes=time_window_minutes)
    
    # Statistics containers
    stats = {
        'total_incidents': 0,
        'incidents_by_type': defaultdict(int),
        'incidents_by_sector': defaultdict(int),
        'errors': [],
        'addressed_incidents': 0,
        'unaddressed_incidents': 0
    }
    
    # Read and analyze logs
    with open(log_file, 'r') as f:
        for line in f:
            try:
                # Parse log entry
                timestamp_str = line.split(' - ')[0]
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
                
                # Skip old entries
                if timestamp < cutoff_time:
                    continue
                
                # Analyze log entry
                if "Successfully logged incident" in line:
                    stats['total_incidents'] += 1
                    # Extract incident type and sector
                    if "Type:" in line and "Sector:" in line:
                        incident_type = line.split("Type: ")[1].split(",")[0]
                        sector = line.split("Sector: ")[1].split("}")[0]
                        stats['incidents_by_type'][incident_type] += 1
                        stats['incidents_by_sector'][sector] += 1
                
                elif "marked as addressed" in line:
                    stats['addressed_incidents'] += 1
                
                elif "ERROR" in line:
                    stats['errors'].append(line.strip())
                
                elif "Retrieved" in line and "unaddressed incidents" in line:
                    count = int(line.split("Retrieved ")[1].split(" ")[0])
                    stats['unaddressed_incidents'] = count
                
            except Exception as e:
                print(f"Error parsing log line: {e}")
                continue
    
    # Generate report
    report = {
        'analysis_time': current_time.strftime('%Y-%m-%d %H:%M:%S'),
        'time_window_minutes': time_window_minutes,
        'statistics': {
            'total_incidents': stats['total_incidents'],
            'incidents_by_type': dict(stats['incidents_by_type']),
            'incidents_by_sector': dict(stats['incidents_by_sector']),
            'addressed_incidents': stats['addressed_incidents'],
            'unaddressed_incidents': stats['unaddressed_incidents'],
            'error_count': len(stats['errors'])
        },
        'recent_errors': stats['errors'][-5:] if stats['errors'] else []  # Last 5 errors
    }
    
    return report

def monitor_logs(interval_seconds=300):  # 5 minutes default
    """Continuously monitor logs and print updates"""
    print("Starting log monitoring...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            print("\n" + "="*50)
            print(f"Log Analysis at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*50)
            
            report = analyze_logs()
            if report:
                print(json.dumps(report, indent=2))
            else:
                print("No log data available")
            
            print("\nWaiting for next update...")
            time.sleep(interval_seconds)
            
    except KeyboardInterrupt:
        print("\nStopping log monitoring")

if __name__ == "__main__":
    monitor_logs() 