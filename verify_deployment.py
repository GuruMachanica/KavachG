#!/usr/bin/env python3
"""
KavachG System Deployment Verification Script

This script checks if all components of the KavachG system are running properly.
It verifies connectivity to:
- Frontend server
- Backend API
- MongoDB database
- ML system components
"""

import os
import sys
import json
import time
import subprocess
import platform
import requests
from datetime import datetime
from urllib.parse import urlparse

# Configuration
FRONTEND_URL = "http://localhost:3000"
BACKEND_URL = "http://localhost:5000"
MONGODB_URI = "mongodb://localhost:27017/safety_monitoring"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"

class VerificationError(Exception):
    """Custom exception for verification failures."""
    pass

class Colors:
    """Terminal colors for pretty output."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print a colored header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}=== {text} ==={Colors.ENDC}\n")

def print_result(text, success=True):
    """Print a colored result."""
    if success:
        print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")
    else:
        print(f"{Colors.RED}✗ {text}{Colors.ENDC}")

def check_connection(url, description, timeout=5):
    """Check if a service is running by making a connection to it."""
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        print_result(f"{description} is running ({url})")
        return True
    except requests.RequestException as e:
        print_result(f"{description} is not accessible ({url}): {str(e)}", False)
        return False

def check_mongodb():
    """Check if MongoDB is running and accessible."""
    try:
        # Parse MongoDB URI
        uri = urlparse(MONGODB_URI)
        host = uri.hostname or "localhost"
        port = uri.port or 27017
        
        # Use different commands based on the platform
        if platform.system() == "Windows":
            result = subprocess.run(
                f"ping -n 1 -w 1000 {host}", 
                shell=True, 
                capture_output=True, 
                text=True
            )
            if result.returncode != 0:
                print_result(f"MongoDB host {host} is not reachable", False)
                return False
                
            # Try connecting to the MongoDB port
            try:
                import socket
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1)
                s.connect((host, port))
                s.close()
                print_result(f"MongoDB is running ({host}:{port})")
                return True
            except (socket.timeout, socket.error):
                print_result(f"MongoDB port {port} is not accessible", False)
                return False
        else:
            # Linux/macOS approach
            result = subprocess.run(
                f"nc -z -w1 {host} {port}", 
                shell=True, 
                capture_output=True, 
                text=True
            )
            if result.returncode == 0:
                print_result(f"MongoDB is running ({host}:{port})")
                return True
            else:
                print_result(f"MongoDB is not accessible ({host}:{port})", False)
                return False
    except Exception as e:
        print_result(f"Error checking MongoDB: {str(e)}", False)
        return False

def check_backend_api():
    """Check various endpoints on the backend API."""
    try:
        # Check API health endpoint
        health_check = check_connection(f"{BACKEND_URL}/api/health", "Backend API health check")
        if not health_check:
            return False
        
        # Try to authenticate with the API
        try:
            auth_response = requests.post(
                f"{BACKEND_URL}/api/users/login",
                json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
                timeout=5
            )
            
            if auth_response.status_code == 200:
                print_result("Backend authentication is working")
                # Get the token for further requests
                token = auth_response.json().get('data', {}).get('token')
                
                if token:
                    # Try to get incidents with the token
                    incidents_response = requests.get(
                        f"{BACKEND_URL}/api/incidents",
                        headers={"Authorization": f"Bearer {token}"},
                        timeout=5
                    )
                    
                    if incidents_response.status_code == 200:
                        print_result("Backend API incidents endpoint is working")
                        return True
                    else:
                        print_result(f"Backend API incidents endpoint returned: {incidents_response.status_code}", False)
                else:
                    print_result("Couldn't get authentication token from response", False)
            else:
                print_result(f"Backend authentication failed: {auth_response.status_code}", False)
        except requests.RequestException as e:
            print_result(f"Error testing backend authentication: {str(e)}", False)
        
        return health_check
    except Exception as e:
        print_result(f"Error checking backend API: {str(e)}", False)
        return False

def check_frontend():
    """Check if the frontend is running."""
    return check_connection(FRONTEND_URL, "Frontend server")

def check_processes():
    """Check if expected processes are running."""
    print_header("Checking System Processes")
    
    processes_to_check = {
        "node": "Backend or Frontend",
        "python": "ML System"
    }
    
    for process, description in processes_to_check.items():
        try:
            if platform.system() == "Windows":
                result = subprocess.run(
                    f"tasklist /FI \"IMAGENAME eq {process}*\"", 
                    shell=True, 
                    capture_output=True, 
                    text=True
                )
                if process in result.stdout:
                    print_result(f"{description} processes are running")
                else:
                    print_result(f"No {description} processes found", False)
            else:
                # Linux/macOS
                result = subprocess.run(
                    f"ps aux | grep {process} | grep -v grep", 
                    shell=True, 
                    capture_output=True, 
                    text=True
                )
                if result.returncode == 0:
                    print_result(f"{description} processes are running")
                else:
                    print_result(f"No {description} processes found", False)
        except Exception as e:
            print_result(f"Error checking {description} processes: {str(e)}", False)

def main():
    """Run all verification checks."""
    print("\n" + "="*80)
    print(f"{Colors.BOLD}KavachG System Deployment Verification{Colors.ENDC}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    all_checks_passed = True
    
    # Check processes
    check_processes()
    
    # Check MongoDB
    print_header("Checking MongoDB")
    mongodb_running = check_mongodb()
    all_checks_passed = all_checks_passed and mongodb_running
    
    # Check backend
    print_header("Checking Backend API")
    backend_running = check_backend_api()
    all_checks_passed = all_checks_passed and backend_running
    
    # Check frontend
    print_header("Checking Frontend")
    frontend_running = check_frontend()
    all_checks_passed = all_checks_passed and frontend_running
    
    # Print summary
    print("\n" + "="*80)
    print(f"{Colors.BOLD}Verification Summary{Colors.ENDC}")
    print("="*80)
    
    if all_checks_passed:
        print(f"\n{Colors.GREEN}{Colors.BOLD}All KavachG system components are running correctly!{Colors.ENDC}")
        print("\nYou can access the dashboard at: " + FRONTEND_URL)
        print("Login with: " + ADMIN_EMAIL + " / " + ADMIN_PASSWORD)
        return 0
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}Some KavachG system components are not running correctly.{Colors.ENDC}")
        
        # Provide troubleshooting guidance
        print("\nTroubleshooting steps:")
        
        if not mongodb_running:
            print(f"{Colors.BLUE}- Make sure MongoDB is installed and running{Colors.ENDC}")
            print("  Windows: Check MongoDB service in Services")
            print("  Linux: Run 'sudo systemctl status mongodb'")
            print("  macOS: Run 'brew services list'")
        
        if not backend_running:
            print(f"{Colors.BLUE}- Check the backend server{Colors.ENDC}")
            print("  Navigate to the backend directory and run:")
            print("  node src/server-sqlite.js")
        
        if not frontend_running:
            print(f"{Colors.BLUE}- Check the frontend server{Colors.ENDC}")
            print("  Navigate to the FrontEnd/FrontEnd directory and run:")
            print("  npm run dev")
        
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nVerification cancelled by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.RED}Error during verification: {str(e)}{Colors.ENDC}")
        sys.exit(1) 