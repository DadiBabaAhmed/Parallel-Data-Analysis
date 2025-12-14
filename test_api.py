#!/usr/bin/env python3
"""
Test suite to verify:
1. Web API containerization
2. Web API health check
3. Web API responds to endpoints
4. Website API integration
"""

import requests
import json
import time
import subprocess
import sys
from datetime import datetime

class APITester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.results = []
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def log_result(self, test_name, passed, message=""):
        status = "PASS" if passed else "FAIL"
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "timestamp": self.timestamp
        }
        self.results.append(result)
        print(f"[{status}] {test_name}: {message}")
        return passed
    
    def test_health_check(self):
        """Test: API health endpoint responds"""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=5)
            passed = response.status_code == 200
            return self.log_result(
                "Health Check",
                passed,
                f"Status: {response.status_code}" if passed else f"Status: {response.status_code}"
            )
        except Exception as e:
            return self.log_result("Health Check", False, str(e))
    
    def test_hosts_endpoint(self):
        """Test: /api/hosts endpoint returns container links"""
        try:
            response = requests.get(f"{self.base_url}/api/hosts", timeout=5)
            passed = response.status_code == 200 and isinstance(response.json(), list)
            data = response.json() if passed else {}
            return self.log_result(
                "Hosts Endpoint",
                passed,
                f"Returned {len(data)} hosts" if passed else "Invalid response"
            )
        except Exception as e:
            return self.log_result("Hosts Endpoint", False, str(e))
    
    def test_input_files_endpoint(self):
        """Test: /api/input-files endpoint lists available input files"""
        try:
            response = requests.get(f"{self.base_url}/api/input-files", timeout=5)
            passed = response.status_code == 200 and "files" in response.json()
            files = response.json().get("files", [])
            return self.log_result(
                "Input Files Endpoint",
                passed,
                f"Found {len(files)} input files" if passed else "Invalid response"
            )
        except Exception as e:
            return self.log_result("Input Files Endpoint", False, str(e))
    
    def test_results_endpoint(self):
        """Test: /api/results endpoint responds"""
        try:
            response = requests.get(f"{self.base_url}/api/results", timeout=5)
            passed = response.status_code == 200
            return self.log_result(
                "Results Endpoint",
                passed,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            return self.log_result("Results Endpoint", False, str(e))
    
    def test_jobs_endpoint(self):
        """Test: /api/jobs endpoint lists jobs"""
        try:
            response = requests.get(f"{self.base_url}/api/jobs", timeout=5)
            passed = response.status_code == 200 and isinstance(response.json(), dict)
            return self.log_result(
                "Jobs Endpoint",
                passed,
                "Jobs retrieved" if passed else "Invalid response"
            )
        except Exception as e:
            return self.log_result("Jobs Endpoint", False, str(e))
    
    def test_cors_headers(self):
        """Test: API responds with CORS headers"""
        try:
            response = requests.options(f"{self.base_url}/api/hosts", timeout=5)
            has_cors = "Access-Control-Allow-Origin" in response.headers
            return self.log_result(
                "CORS Headers",
                has_cors,
                "CORS headers present" if has_cors else "No CORS headers found"
            )
        except Exception as e:
            return self.log_result("CORS Headers", False, str(e))
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*60)
        print("WEB API INTEGRATION TESTS")
        print("="*60 + "\n")
        
        self.test_health_check()
        self.test_hosts_endpoint()
        self.test_input_files_endpoint()
        self.test_results_endpoint()
        self.test_jobs_endpoint()
        self.test_cors_headers()
        
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for r in self.results if r["status"] == "PASS")
        failed = sum(1 for r in self.results if r["status"] == "FAIL")
        total = len(self.results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        print("="*60 + "\n")
        
        return failed == 0

if __name__ == "__main__":
    # Check if API is accessible
    print("Attempting to connect to Web API at http://localhost:5000...")
    print("Make sure Docker containers are running with: docker-compose up -d\n")
    
    tester = APITester()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)
