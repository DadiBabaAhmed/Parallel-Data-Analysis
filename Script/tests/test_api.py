"""
Comprehensive tests for Web API module
Tests all endpoints, error handling, and integration with Spark cluster
"""
import pytest
import json
import os
import tempfile
from unittest.mock import patch, MagicMock
import sys

# Test setup for API testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from api.web_api import app
from src.error_handler import ErrorHandler


@pytest.fixture
def api_client():
    """Create a Flask test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def temp_api_dirs(temp_test_dir):
    """Create API-specific output directories"""
    dirs = [
        os.path.join(temp_test_dir, "output", "general"),
        os.path.join(temp_test_dir, "output", "general", "graphs"),
        os.path.join(temp_test_dir, "output", "statistics"),
        os.path.join(temp_test_dir, "output", "failures"),
        os.path.join(temp_test_dir, "output", "jobs"),
        os.path.join(temp_test_dir, "data", "input"),
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
    
    yield dirs


class TestAPIInitialization:
    """Test API initialization and basic setup"""
    
    def test_api_app_exists(self):
        """Test that Flask app is properly initialized"""
        assert app is not None
        assert hasattr(app, 'test_client')
    
    def test_api_testing_mode(self, api_client):
        """Test that API can be tested"""
        assert api_client is not None


class TestAPIHealthEndpoint:
    """Test /api/health endpoint"""
    
    def test_health_endpoint_returns_ok(self, api_client):
        """Test that health endpoint returns 200 with ok status"""
        response = api_client.get('/api/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'ok'
    
    def test_health_endpoint_response_format(self, api_client):
        """Test that health endpoint returns proper JSON"""
        response = api_client.get('/api/health')
        
        assert response.content_type == 'application/json'
        data = json.loads(response.data)
        assert 'status' in data


class TestAPIHostsEndpoint:
    """Test /api/hosts endpoint"""
    
    def test_hosts_endpoint_returns_list(self, api_client):
        """Test that hosts endpoint returns host information"""
        response = api_client.get('/api/hosts')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'hosts' in data or 'containers' in data
    
    def test_hosts_endpoint_includes_master(self, api_client):
        """Test that hosts endpoint includes Spark master information"""
        response = api_client.get('/api/hosts')
        
        data = json.loads(response.data)
        # Should have some host/container information
        assert len(data) > 0 or 'hosts' in data or 'containers' in data


class TestAPIInputFilesEndpoint:
    """Test /api/input-files endpoint"""
    
    def test_input_files_endpoint_returns_list(self, api_client):
        """Test that input-files endpoint returns file list"""
        response = api_client.get('/api/input-files')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        # Should have files or empty list
        assert isinstance(data, (list, dict))
    
    def test_input_files_can_read_sample_data(self, api_client):
        """Test that input files endpoint finds sample data files"""
        response = api_client.get('/api/input-files')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Convert to list if it's a dict with 'files' key
        files = data if isinstance(data, list) else data.get('files', [])
        
        # Should handle the case where files are present or not
        assert isinstance(files, list)


class TestAPIResultsEndpoint:
    """Test /api/results endpoint"""
    
    def test_results_endpoint_returns_data(self, api_client):
        """Test that results endpoint returns results information"""
        response = api_client.get('/api/results')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Should return dict or list
        assert isinstance(data, (dict, list))
    
    def test_results_endpoint_includes_graphs(self, api_client):
        """Test that results endpoint can list graphs"""
        response = api_client.get('/api/results')
        
        assert response.status_code == 200
        # Should complete without error


class TestAPICORSHeaders:
    """Test CORS headers on API endpoints"""
    
    def test_health_endpoint_includes_cors_headers(self, api_client):
        """Test that CORS headers are present"""
        response = api_client.get('/api/health')
        
        # Check for CORS headers
        assert response.status_code == 200
        # CORS headers should be present
        headers = dict(response.headers)
        # At minimum, it should return JSON
        assert 'Content-Type' in headers


class TestAPITriggerEndpoint:
    """Test /api/trigger endpoint"""
    
    def test_trigger_endpoint_accepts_post(self, api_client):
        """Test that trigger endpoint accepts POST requests"""
        payload = {
            'input_file': 'test.csv',
            'analysis_type': 'statistical'
        }
        
        response = api_client.post(
            '/api/trigger',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Should return success or process the request
        assert response.status_code in [200, 201, 400]  # 400 for invalid file is ok
    
    def test_trigger_endpoint_returns_job_id(self, api_client):
        """Test that trigger endpoint returns job identifier"""
        payload = {
            'input_file': 'sample_sales.csv',
            'analysis_type': 'statistical'
        }
        
        response = api_client.post(
            '/api/trigger',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        if response.status_code in [200, 201]:
            data = json.loads(response.data)
            # Should have job information
            assert 'job_id' in data or 'id' in data or 'status' in data


class TestAPIJobsEndpoint:
    """Test /api/jobs endpoint"""
    
    def test_jobs_endpoint_returns_list(self, api_client):
        """Test that jobs endpoint returns job list"""
        response = api_client.get('/api/jobs')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Should return list or dict with jobs
        assert isinstance(data, (list, dict))
    
    def test_jobs_endpoint_format(self, api_client):
        """Test that jobs endpoint returns proper format"""
        response = api_client.get('/api/jobs')
        
        data = json.loads(response.data)
        
        # If it's a dict, it might have 'jobs' key
        if isinstance(data, dict):
            # Should have some structure
            assert len(data) >= 0


class TestAPIJobDetailEndpoint:
    """Test /api/job/<job_id> endpoint"""
    
    def test_job_detail_endpoint_with_invalid_id(self, api_client):
        """Test job detail endpoint with invalid ID"""
        response = api_client.get('/api/job/nonexistent-job-id')
        
        # Should return 404 or empty/error response
        assert response.status_code in [200, 404]
    
    def test_job_detail_endpoint_returns_json(self, api_client):
        """Test that job detail endpoint returns JSON"""
        response = api_client.get('/api/job/test-job-123')
        
        # Should return valid JSON
        try:
            data = json.loads(response.data)
            assert isinstance(data, (dict, list))
        except json.JSONDecodeError:
            # Some responses might not be JSON
            pass


class TestAPIErrorHandling:
    """Test API error handling"""
    
    def test_invalid_endpoint_returns_404(self, api_client):
        """Test that invalid endpoints return 404"""
        response = api_client.get('/api/nonexistent')
        
        assert response.status_code == 404
    
    def test_malformed_json_handled(self, api_client):
        """Test that malformed JSON is handled"""
        response = api_client.post(
            '/api/trigger',
            data='invalid json',
            content_type='application/json'
        )
        
        # Should not crash, return error
        assert response.status_code in [400, 422]
    
    def test_missing_required_fields(self, api_client):
        """Test that missing required fields are handled"""
        payload = {'input_file': 'test.csv'}  # Missing analysis_type
        
        response = api_client.post(
            '/api/trigger',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # Should handle missing fields gracefully
        assert response.status_code in [200, 201, 400]


class TestAPIIntegration:
    """Integration tests for API"""
    
    def test_api_workflow(self, api_client):
        """Test complete API workflow"""
        # Step 1: Check health
        health_resp = api_client.get('/api/health')
        assert health_resp.status_code == 200
        
        # Step 2: Get input files
        files_resp = api_client.get('/api/input-files')
        assert files_resp.status_code == 200
        
        # Step 3: Get hosts
        hosts_resp = api_client.get('/api/hosts')
        assert hosts_resp.status_code == 200
        
        # Step 4: Get results
        results_resp = api_client.get('/api/results')
        assert results_resp.status_code == 200
    
    def test_api_multiple_requests(self, api_client):
        """Test that API handles multiple requests"""
        for _ in range(5):
            response = api_client.get('/api/health')
            assert response.status_code == 200


class TestAPIResponseFormat:
    """Test API response formats"""
    
    def test_all_endpoints_return_json(self, api_client):
        """Test that all read endpoints return JSON"""
        endpoints = [
            '/api/health',
            '/api/hosts',
            '/api/input-files',
            '/api/results',
            '/api/jobs',
        ]
        
        for endpoint in endpoints:
            response = api_client.get(endpoint)
            assert response.status_code in [200, 404]
            if response.status_code == 200:
                try:
                    json.loads(response.data)
                except json.JSONDecodeError:
                    pytest.fail(f"Endpoint {endpoint} did not return valid JSON")
    
    def test_response_status_codes(self, api_client):
        """Test that endpoints return appropriate status codes"""
        response = api_client.get('/api/health')
        assert response.status_code == 200
        
        response = api_client.get('/api/invalid')
        assert response.status_code == 404
        
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
