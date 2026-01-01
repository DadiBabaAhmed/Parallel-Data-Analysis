#!/usr/bin/env python3
"""
Test execution helper script
Provides convenient test running with various configurations

Usage:
    python run_tests.py                 # Run all tests
    python run_tests.py unit            # Run unit tests only
    python run_tests.py integration     # Run integration tests only
    python run_tests.py coverage        # Run with coverage report
    python run_tests.py quick           # Run quick smoke tests
    python run_tests.py verbose         # Run with verbose output
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description=""):
    """Run a command and report results"""
    if description:
        print(f"\n{'='*70}")
        print(f"  {description}")
        print(f"{'='*70}\n")
    
    try:
        result = subprocess.run(cmd, shell=True, cwd="Script")
        return result.returncode == 0
    except Exception as e:
        print(f"Error running command: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    return run_command(
        "pytest tests/ -v",
        "Running All Tests"
    )


def run_unit_tests():
    """Run only unit tests"""
    return run_command(
        "pytest tests/ -m unit -v",
        "Running Unit Tests"
    )


def run_integration_tests():
    """Run only integration tests"""
    return run_command(
        "pytest tests/ -m integration -v",
        "Running Integration Tests"
    )


def run_smoke_tests():
    """Run smoke tests (quick tests)"""
    return run_command(
        "pytest tests/ -m smoke -v",
        "Running Smoke Tests"
    )


def run_with_coverage():
    """Run tests with coverage report"""
    commands = [
        "pytest tests/ --cov=src --cov-report=term-missing --cov-report=html -v",
        "echo \nCoverage report generated in htmlcov/index.html"
    ]
    
    success = run_command(
        " && ".join(commands),
        "Running Tests with Coverage"
    )
    
    if success:
        print("\n✓ Coverage report available: htmlcov/index.html")
    
    return success


def run_quick_tests():
    """Run quick tests without slow tests"""
    return run_command(
        "pytest tests/ -m 'not slow' -v --tb=short",
        "Running Quick Tests (excluding slow tests)"
    )


def run_specific_test(test_name):
    """Run a specific test"""
    return run_command(
        f"pytest tests/ -k '{test_name}' -v",
        f"Running Tests Matching: {test_name}"
    )


def run_verbose():
    """Run tests with verbose output"""
    return run_command(
        "pytest tests/ -vv -s",
        "Running Tests (Verbose Output)"
    )


def run_api_tests():
    """Run only API tests"""
    return run_command(
        "pytest tests/test_api.py -v",
        "Running API Tests"
    )


def run_loader_tests():
    """Run only data loader tests"""
    return run_command(
        "pytest tests/test_data_loader.py -v",
        "Running DataLoader Tests"
    )


def run_analyzer_tests():
    """Run only analyzer tests"""
    return run_command(
        "pytest tests/test_analyzer.py -v",
        "Running DataAnalyzer Tests"
    )


def run_graph_tests():
    """Run only graph tests"""
    return run_command(
        "pytest tests/test_graphs.py -v",
        "Running GraphGenerator Tests"
    )


def print_help():
    """Print help message"""
    print("""
Test Execution Helper

Usage: python run_tests.py [command]

Commands:
    all             Run all tests (default)
    unit            Run unit tests only
    integration     Run integration tests only
    smoke           Run smoke tests (quick)
    coverage        Run with coverage report
    quick           Run quick tests (exclude slow)
    verbose         Run with verbose output
    api             Run API tests only
    loader          Run DataLoader tests only
    analyzer        Run DataAnalyzer tests only
    graphs          Run GraphGenerator tests only
    <test_name>     Run tests matching a name pattern
    help            Show this help message

Examples:
    python run_tests.py                    # Run all tests
    python run_tests.py coverage           # Generate coverage report
    python run_tests.py test_load_csv      # Run tests matching 'test_load_csv'
    python run_tests.py unit               # Run only unit tests

Environment:
    PYTEST_OPTIONS - Additional pytest options to pass
    
Results:
    Test output goes to console
    Coverage report (if generated) goes to: htmlcov/index.html
    """)


def main():
    """Main entry point"""
    if len(sys.argv) < 2 or sys.argv[1] in ['help', '-h', '--help']:
        print_help()
        return 0
    
    command = sys.argv[1].lower()
    
    commands_map = {
        'all': run_all_tests,
        'unit': run_unit_tests,
        'integration': run_integration_tests,
        'smoke': run_smoke_tests,
        'coverage': run_with_coverage,
        'quick': run_quick_tests,
        'verbose': run_verbose,
        'api': run_api_tests,
        'loader': run_loader_tests,
        'analyzer': run_analyzer_tests,
        'graphs': run_graph_tests,
    }
    
    if command in commands_map:
        success = commands_map[command]()
    else:
        # Try to run as pattern match
        success = run_specific_test(command)
    
    # Print summary
    print(f"\n{'='*70}")
    if success:
        print("  ✓ Tests passed successfully!")
    else:
        print("  ✗ Some tests failed. Please review output above.")
    print(f"{'='*70}\n")
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
