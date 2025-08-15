@echo off
REM Database Initialization Script for Windows
REM AI Research Framework

echo ========================================
echo AI Research Framework - Database Setup
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.11+ and try again
    pause
    exit /b 1
)

REM Check if UV is available
uv --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] UV is not installed
    echo Using pip instead of UV for this script
    set USE_UV=false
) else (
    echo [INFO] UV detected, using UV for execution
    set USE_UV=true
)

REM Parse command line arguments
set RESET_DB=false
set SAMPLE_DATA=false
set VERIFY_ONLY=false

:parse_args
if "%1"=="--reset" (
    set RESET_DB=true
    shift
    goto parse_args
)
if "%1"=="--sample-data" (
    set SAMPLE_DATA=true
    shift
    goto parse_args
)
if "%1"=="--verify-only" (
    set VERIFY_ONLY=true
    shift
    goto parse_args
)
if "%1"=="--help" (
    echo Usage: init_db.bat [options]
    echo.
    echo Options:
    echo   --reset       Drop existing tables and recreate them
    echo   --sample-data Insert sample data for testing
    echo   --verify-only Only verify database structure
    echo   --help        Show this help message
    echo.
    pause
    exit /b 0
)
if not "%1"=="" (
    shift
    goto parse_args
)

REM Create data directory if it doesn't exist
if not exist "data" (
    echo [INFO] Creating data directory...
    mkdir data
)

REM Create logs directory if it doesn't exist
if not exist "logs" (
    echo [INFO] Creating logs directory...
    mkdir logs
)

REM Set environment variables
set PYTHONPATH=%CD%\src;%PYTHONPATH%
set DATABASE_URL=sqlite+aiosqlite:///%CD%\data\research.db

REM Build command arguments
set CMD_ARGS=
if "%RESET_DB%"=="true" set CMD_ARGS=%CMD_ARGS% --reset
if "%SAMPLE_DATA%"=="true" set CMD_ARGS=%CMD_ARGS% --sample-data
if "%VERIFY_ONLY%"=="true" set CMD_ARGS=%CMD_ARGS% --verify-only

echo [INFO] Initializing database...
echo [INFO] Database location: %DATABASE_URL%

REM Run the initialization script
if "%USE_UV%"=="true" (
    echo [INFO] Running with UV...
    uv run python init_db.py %CMD_ARGS%
) else (
    echo [INFO] Running with Python...
    python init_db.py %CMD_ARGS%
)

if errorlevel 1 (
    echo.
    echo [ERROR] Database initialization failed!
    echo Check the logs above for details.
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Database initialization completed!
echo.

if "%VERIFY_ONLY%"=="false" (
    echo Next steps:
    echo 1. Review and update the .env file with your configuration
    echo 2. Start the application: 
    echo    - With Docker: docker-compose up --build
    echo    - With UV: uv run uvicorn ai_research_framework.api.main:app --reload
    echo 3. Visit http://localhost:8000/docs for API documentation
    echo 4. Run tests: scripts\run_tests_windows.bat
    echo.
)

pause

