#!/usr/bin/env python
"""
Test runner script for the AI Research Framework.
"""

import sys
import subprocess
from pathlib import Path

def run_tests(args=None):
    """Run pytest with the specified arguments."""
    
    # Default arguments if none provided
    if args is None:
        args = []
    
    # Build the command
    cmd = ["pytest"] + args
    
    print("=" * 60)
    print("AI Research Framework - Test Runner")
    print("=" * 60)
    print(f"Running: {' '.join(cmd)}")
    print("-" * 60)
    
    # Run the tests
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    
    return result.returncode

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run tests for AI Research Framework")
    parser.add_argument(
        "--unit",
        action="store_true",
        help="Run only unit tests"
    )
    parser.add_argument(
        "--integration",
        action="store_true",
        help="Run only integration tests"
    )
    parser.add_argument(
        "--api",
        action="store_true",
        help="Run only API tests"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run with coverage report"
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Run tests in parallel"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick tests only (exclude slow tests)"
    )
    parser.add_argument(
        "tests",
        nargs="*",
        help="Specific test files or directories to run"
    )
    
    args = parser.parse_args()
    
    # Build pytest arguments
    pytest_args = []
    
    # Add marker filters
    markers = []
    if args.unit:
        markers.append("unit")
    if args.integration:
        markers.append("integration")
    if args.api:
        markers.append("api")
    
    if markers:
        pytest_args.extend(["-m", " or ".join(markers)])
    
    # Exclude slow tests if quick mode
    if args.quick:
        pytest_args.extend(["-m", "not slow"])
    
    # Add coverage if requested
    if args.coverage:
        pytest_args.extend([
            "--cov=src/ai_research_framework",
            "--cov-report=term-missing",
            "--cov-report=html"
        ])
    
    # Add parallel execution if requested
    if args.parallel:
        pytest_args.extend(["-n", "auto"])
    
    # Add verbose if requested
    if args.verbose:
        pytest_args.append("-vv")
    
    # Add specific test paths if provided
    if args.tests:
        pytest_args.extend(args.tests)
    
    # Run the tests
    exit_code = run_tests(pytest_args)
    
    # Print summary
    print("-" * 60)
    if exit_code == 0:
        print("✅ All tests passed!")
    else:
        print(f"❌ Tests failed with exit code: {exit_code}")
    print("=" * 60)
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())
