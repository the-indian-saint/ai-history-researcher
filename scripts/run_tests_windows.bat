@echo off
REM AI Research Framework Test Automation Script for Windows
REM This script runs comprehensive tests for the AI Research Framework on Windows

setlocal enabledelayedexpansion

REM Colors for output (Windows compatible)
set "INFO=[INFO]"
set "SUCCESS=[SUCCESS]"
set "WARNING=[WARNING]"
set "ERROR=[ERROR]"

echo %INFO% Starting AI Research Framework Test Suite
echo ========================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo %ERROR% Python is not installed or not in PATH
    exit /b 1
)

REM Check if pip is installed
pip --version >nul 2>&1
if errorlevel 1 (
    echo %ERROR% pip is not installed or not in PATH
    exit /b 1
)

echo %SUCCESS% Prerequisites check passed

REM Install dependencies
echo %INFO% Installing test dependencies...
pip install -q pytest pytest-asyncio pytest-cov pytest-html pytest-json-report
pip install -q loguru fastapi uvicorn sqlalchemy aiosqlite databases
pip install -q beautifulsoup4 requests aiofiles python-multipart

if errorlevel 1 (
    echo %ERROR% Failed to install dependencies
    exit /b 1
)

echo %SUCCESS% Dependencies installed

REM Create necessary directories
echo %INFO% Setting up test environment...
if not exist "data" mkdir data
if not exist "logs" mkdir logs
if not exist "temp" mkdir temp
if not exist "reports" mkdir reports
if not exist "htmlcov" mkdir htmlcov

REM Set environment variables
set TESTING=true
set DATABASE_URL=sqlite+aiosqlite:///:memory:
set LOG_LEVEL=DEBUG
set PYTHONPATH=%CD%\src;%PYTHONPATH%

echo %SUCCESS% Test environment setup complete

REM Run unit tests
echo %INFO% Running unit tests...
python -m pytest tests\unit ^
    -v ^
    --tb=short ^
    --cov=src\ai_research_framework ^
    --cov-report=html:htmlcov ^
    --cov-report=xml:coverage.xml ^
    --cov-report=term-missing ^
    --html=reports\unit_test_report.html ^
    --self-contained-html ^
    --json-report ^
    --json-report-file=reports\unit_test_report.json

if errorlevel 1 (
    echo %WARNING% Some unit tests failed
) else (
    echo %SUCCESS% Unit tests complete
)

REM Run integration tests
echo %INFO% Running integration tests...
python -m pytest tests\integration ^
    -v ^
    --tb=short ^
    --maxfail=5 ^
    --html=reports\integration_test_report.html ^
    --self-contained-html ^
    --json-report ^
    --json-report-file=reports\integration_test_report.json

if errorlevel 1 (
    echo %WARNING% Some integration tests failed
) else (
    echo %SUCCESS% Integration tests complete
)

REM Run API tests
echo %INFO% Running API tests...
python -m pytest tests\integration\test_api_endpoints.py ^
    -v ^
    --tb=short ^
    --html=reports\api_test_report.html ^
    --self-contained-html

if errorlevel 1 (
    echo %WARNING% Some API tests failed
) else (
    echo %SUCCESS% API tests complete
)

REM Generate test report
echo %INFO% Generating comprehensive test report...

echo # AI Research Framework Test Report > reports\test_summary.md
echo. >> reports\test_summary.md
echo ## Test Execution Summary >> reports\test_summary.md
echo. >> reports\test_summary.md
echo **Date:** %date% %time% >> reports\test_summary.md
echo **Environment:** Test >> reports\test_summary.md
echo **Platform:** Windows >> reports\test_summary.md
echo. >> reports\test_summary.md
echo ## Test Results >> reports\test_summary.md
echo. >> reports\test_summary.md
echo ### Unit Tests >> reports\test_summary.md
echo - Location: `tests\unit\` >> reports\test_summary.md
echo - Report: [Unit Test Report](unit_test_report.html) >> reports\test_summary.md
echo - Coverage: [Coverage Report](../htmlcov/index.html) >> reports\test_summary.md
echo. >> reports\test_summary.md
echo ### Integration Tests >> reports\test_summary.md
echo - Location: `tests\integration\` >> reports\test_summary.md
echo - Report: [Integration Test Report](integration_test_report.html) >> reports\test_summary.md
echo. >> reports\test_summary.md
echo ### API Tests >> reports\test_summary.md
echo - Location: `tests\integration\test_api_endpoints.py` >> reports\test_summary.md
echo - Report: [API Test Report](api_test_report.html) >> reports\test_summary.md
echo. >> reports\test_summary.md
echo ## Coverage Information >> reports\test_summary.md
echo. >> reports\test_summary.md
echo Coverage reports are available in the `htmlcov\` directory. >> reports\test_summary.md
echo. >> reports\test_summary.md
echo ## Next Steps >> reports\test_summary.md
echo. >> reports\test_summary.md
echo 1. Review failed tests and fix issues >> reports\test_summary.md
echo 2. Improve test coverage for areas below 80%% >> reports\test_summary.md
echo 3. Run tests regularly during development >> reports\test_summary.md

echo %SUCCESS% Test report generated: reports\test_summary.md

echo %SUCCESS% All tests completed!
echo %INFO% Check the reports\ directory for detailed results
echo %INFO% Open reports\unit_test_report.html in your browser to view test results
echo %INFO% Open htmlcov\index.html in your browser to view coverage report

pause

