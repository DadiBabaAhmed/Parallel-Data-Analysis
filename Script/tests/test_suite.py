"""
Complete test suite for Parallel Data Analysis Framework
Includes unit tests, integration tests, and end-to-end tests

Run with: pytest tests/ -v
Run with coverage: pytest tests/ --cov=src --cov-report=html
Run specific tests: pytest tests/test_data_loader.py::TestDataLoaderCSV::test_load_csv_basic -v
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "smoke: mark test as a smoke test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as a performance test"
    )
    config.addinivalue_line(
        "markers", "docker: mark test as requiring Docker"
    )


def pytest_collection_modifyitems(config, items):
    """
    Automatically assign markers to tests based on file names
    """
    for item in items:
        # Mark API tests
        if "test_api" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        
        # Mark loader tests
        elif "test_data_loader" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        
        # Mark analyzer tests
        elif "test_analyzer" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        
        # Mark graph tests
        elif "test_graphs" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        
        # Mark main/smoke tests
        elif "test_main_smoke" in str(item.fspath):
            item.add_marker(pytest.mark.smoke)


# Test summary and collection
def pytest_sessionfinish(session, exitstatus):
    """Print test summary after all tests"""
    print("\n" + "="*70)
    print("TEST SUITE EXECUTION COMPLETED")
    print("="*70)
    print(f"Exit Status: {exitstatus}")
    print("="*70 + "\n")


if __name__ == '__main__':
    # Allow running pytest programmatically
    pytest.main([__file__, '-v', '--tb=short'])


class TestRunner:
    """Small helper used by the top-level suite tests for structured output
    (kept lightweight so pytest collection doesn't fail)."""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def log(self, message, level="INFO"):
        prefix = f"[{level}]"
        print(f"{prefix} {message}")

    def assert_equal(self, actual, expected, message):
        if actual == expected:
            self.log(f"✓ {message}", "PASS")
            self.passed += 1
        else:
            self.log(f"✗ {message}", "FAIL")
            self.log(f"  Expected: {expected}, Got: {actual}", "FAIL")
            self.failed += 1
            self.errors.append(message)

    def assert_true(self, condition, message):
        if condition:
            self.log(f"✓ {message}", "PASS")
            self.passed += 1
        else:
            self.log(f"✗ {message}", "FAIL")
            self.failed += 1
            self.errors.append(message)

    def print_summary(self):
        total = self.passed + self.failed
        percentage = (self.passed / total * 100) if total > 0 else 0
        print(f"\n{'='*60}")
        print(f"TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Passed:  {self.passed}/{total}")
        print(f"Failed:  {self.failed}/{total}")
        print(f"Success: {percentage:.1f}%")
        if self.errors:
            print(f"\nFailed Tests:")
            for error in self.errors:
                print(f"  - {error}")
        print(f"{'='*60}\n")

def test_docker_setup():
    """Test 1: Verify docker-compose configuration"""
    print(f"\n{'='*60}")
    print("TEST 1: Docker Compose Configuration")
    print(f"{'='*60}")
    
    runner = TestRunner()
    
    # Test docker-compose syntax
    try:
        result = subprocess.run(
            ["docker-compose", "config", "--quiet"],
            cwd=str(DOCKER_COMPOSE_DIR),
            capture_output=True,
            timeout=10
        )
        runner.assert_equal(result.returncode, 0, "docker-compose.yml syntax is valid")
    except Exception as e:
        runner.assert_true(False, f"docker-compose syntax check failed: {e}")
    
    # Check for required services
    try:
        result = subprocess.run(
            ["docker-compose", "config"],
            cwd=str(DOCKER_COMPOSE_DIR),
            capture_output=True,
            timeout=10
        )
        config_text = result.stdout.decode()
        runner.assert_true("spark-master" in config_text, "spark-master service exists")
        runner.assert_true("spark-worker" in config_text, "spark-worker services exist")
        runner.assert_true("pda-web-api" in config_text, "web_api service exists")
        runner.assert_true("spark-network" in config_text, "spark-network is configured")
    except Exception as e:
        runner.assert_true(False, f"Failed to parse docker-compose: {e}")
    
    runner.print_summary()
    return runner.passed, runner.failed

def test_web_api_files():
    """Test 2: Verify web_api files and configuration"""
    print(f"\n{'='*60}")
    print("TEST 2: Web API Files & Configuration")
    print(f"{'='*60}")
    
    runner = TestRunner()
    
    script_dir = DOCKER_COMPOSE_DIR
    
    # Check files exist
    runner.assert_true((script_dir / "api" / "web_api.py").exists(), "web_api.py exists")
    runner.assert_true((script_dir / "api" / "__init__.py").exists(), "api/__init__.py exists")
    runner.assert_true((script_dir / "docker" / "Dockerfile").exists(), "Dockerfile exists")
    
    # Check web_api.py content
    try:
        with open(script_dir / "api" / "web_api.py", "r") as f:
            content = f.read()
            runner.assert_true("flask" in content.lower(), "Flask import found")
            runner.assert_true("docker" in content.lower(), "Docker SDK import found")
            runner.assert_true("BASE_DIR" in content, "BASE_DIR configuration found")
    except Exception as e:
        runner.assert_true(False, f"Failed to read web_api.py: {e}")
    
    # Check Dockerfile content
    try:
        with open(script_dir / "docker" / "Dockerfile", "r") as f:
            content = f.read()
            runner.assert_true("flask" in content.lower(), "Flask in Dockerfile requirements")
            runner.assert_true("docker" in content.lower(), "Docker SDK in Dockerfile requirements")
            runner.assert_true("5000" in content, "Port 5000 exposed")
    except Exception as e:
        runner.assert_true(False, f"Failed to read Dockerfile: {e}")
    
    runner.print_summary()
    return runner.passed, runner.failed

def test_website_integration():
    """Test 3: Verify website API integration"""
    print(f"\n{'='*60}")
    print("TEST 3: Website API Integration")
    print(f"{'='*60}")
    
    runner = TestRunner()
    
    website_dir = DOCKER_COMPOSE_DIR.parent / "Web site"
    
    # Check HTML files
    runner.assert_true((website_dir / "index.html").exists(), "index.html exists")
    runner.assert_true((website_dir / "dashboard.html").exists(), "dashboard.html exists")
    runner.assert_true((website_dir / "main.js").exists(), "main.js exists")
    
    # Check main.js for API integration
    try:
        with open(website_dir / "main.js", "r") as f:
            content = f.read()
            runner.assert_true("API_BASE" in content, "API_BASE configuration found")
            runner.assert_true("localhost:5000" in content or "5000" in content, "API port 5000 referenced")
            runner.assert_true("/api/hosts" in content, "API /api/hosts endpoint called")
            runner.assert_true("/api/results" in content, "API /api/results endpoint called")
            runner.assert_true("/api/trigger" in content, "API /api/trigger endpoint called")
            runner.assert_true("triggerAnalysis" in content, "Analysis trigger function found")
    except Exception as e:
        runner.assert_true(False, f"Failed to read main.js: {e}")
    
    # Check index.html structure
    try:
        with open(website_dir / "index.html", "r") as f:
            content = f.read()
            runner.assert_true("<nav" in content, "Navigation element found")
            runner.assert_true("hostsList" in content, "Hosts list element found")
    except Exception as e:
        runner.assert_true(False, f"Failed to read index.html: {e}")
    
    runner.print_summary()
    return runner.passed, runner.failed

def test_api_endpoints():
    """Test 4: Verify API endpoints are responding (requires running docker-compose)"""
    print(f"\n{'='*60}")
    print("TEST 4: API Endpoints (requires docker-compose up)")
    print(f"{'='*60}")
    
    runner = TestRunner()
    
    try:
        # Try to connect to API
        response = requests.get(f"{API_BASE}/api/health", timeout=5)
        runner.assert_equal(response.status_code, 200, "API health endpoint responds")
        
        # Test other endpoints
        endpoints = [
            ("/api/hosts", 200, "Hosts endpoint"),
            ("/api/results", 200, "Results endpoint"),
            ("/api/input-files", 200, "Input files endpoint"),
            ("/api/jobs", 200, "Jobs list endpoint"),
        ]
        
        for endpoint, expected_code, name in endpoints:
            try:
                response = requests.get(f"{API_BASE}{endpoint}", timeout=5)
                runner.assert_equal(response.status_code, expected_code, f"{name} returns {expected_code}")
            except Exception as e:
                runner.assert_true(False, f"{name} is accessible: {e}")
    
    except requests.exceptions.ConnectionError:
        runner.log("⚠ Docker-compose not running - skipping live endpoint tests", "WARN")
        runner.log("To test endpoints, run: docker-compose up", "INFO")
    except Exception as e:
        runner.assert_true(False, f"API endpoint tests failed: {e}")
    
    runner.print_summary()
    return runner.passed, runner.failed

def test_data_directories():
    """Test 5: Verify required data directories exist"""
    print(f"\n{'='*60}")
    print("TEST 5: Data Directory Structure")
    print(f"{'='*60}")
    
    runner = TestRunner()
    
    script_dir = DOCKER_COMPOSE_DIR
    
    required_dirs = [
        ("data/input", "Input data directory"),
        ("output/general", "General output directory"),
        ("output/statistics", "Statistics output directory"),
        ("output/jobs", "Jobs tracking directory"),
    ]
    
    for dir_path, description in required_dirs:
        full_path = script_dir / dir_path
        runner.assert_true(full_path.exists(), f"{description} ({dir_path}) exists")
    
    runner.print_summary()
    return runner.passed, runner.failed

def main():
    print("\n" + "="*60)
    print("PARALLEL DATA ANALYSIS - COMPREHENSIVE TEST SUITE")
    print("="*60)
    
    # Run all tests
    test_results = []
    
    test_results.append(("Docker Setup", test_docker_setup()))
    test_results.append(("Web API Files", test_web_api_files()))
    test_results.append(("Website Integration", test_website_integration()))
    test_results.append(("Data Directories", test_data_directories()))
    test_results.append(("API Endpoints", test_api_endpoints()))
    
    # Overall summary
    print(f"\n{'='*60}")
    print("OVERALL TEST SUMMARY")
    print(f"{'='*60}")
    
    total_passed = 0
    total_failed = 0
    
    for test_name, (passed, failed) in test_results:
        total_passed += passed
        total_failed += failed
        status = "✓ PASS" if failed == 0 else "✗ FAIL"
        print(f"{status} | {test_name}: {passed} passed, {failed} failed")
    
    total = total_passed + total_failed
    percentage = (total_passed / total * 100) if total > 0 else 0
    
    print(f"\nTotal: {total_passed}/{total} tests passed ({percentage:.1f}%)")
    print(f"{'='*60}\n")
    
    # Return exit code
    return 0 if total_failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
