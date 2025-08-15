#!/bin/bash

# Database Initialization Script for Linux/Mac
# AI Research Framework

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Show help
show_help() {
    echo "AI Research Framework - Database Initialization"
    echo "=============================================="
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --reset       Drop existing tables and recreate them"
    echo "  --sample-data Insert sample data for testing"
    echo "  --verify-only Only verify database structure"
    echo "  --help        Show this help message"
    echo ""
}

# Parse command line arguments
RESET_DB=false
SAMPLE_DATA=false
VERIFY_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --reset)
            RESET_DB=true
            shift
            ;;
        --sample-data)
            SAMPLE_DATA=true
            shift
            ;;
        --verify-only)
            VERIFY_ONLY=true
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

print_info "AI Research Framework - Database Setup"
print_info "======================================"

# Check prerequisites
print_info "Checking prerequisites..."

if ! command_exists python3; then
    print_error "Python 3 is not installed"
    exit 1
fi

USE_UV=false
if command_exists uv; then
    print_info "UV detected, using UV for execution"
    USE_UV=true
else
    print_warning "UV not found, using python3 directly"
fi

print_success "Prerequisites check passed"

# Create necessary directories
print_info "Creating directories..."
mkdir -p data logs temp

# Set environment variables
export PYTHONPATH="${PWD}/src:${PYTHONPATH}"
export DATABASE_URL="sqlite+aiosqlite:///${PWD}/data/research.db"

print_info "Database location: ${DATABASE_URL}"

# Build command arguments
CMD_ARGS=""
if [ "$RESET_DB" = true ]; then
    CMD_ARGS="$CMD_ARGS --reset"
fi
if [ "$SAMPLE_DATA" = true ]; then
    CMD_ARGS="$CMD_ARGS --sample-data"
fi
if [ "$VERIFY_ONLY" = true ]; then
    CMD_ARGS="$CMD_ARGS --verify-only"
fi

# Run the initialization script
print_info "Initializing database..."

if [ "$USE_UV" = true ]; then
    print_info "Running with UV..."
    uv run python init_db.py $CMD_ARGS
else
    print_info "Running with Python..."
    python3 init_db.py $CMD_ARGS
fi

if [ $? -eq 0 ]; then
    print_success "Database initialization completed!"
    
    if [ "$VERIFY_ONLY" = false ]; then
        echo ""
        print_info "Next steps:"
        echo "1. Review and update the .env file with your configuration"
        echo "2. Start the application:"
        echo "   - With Make: make serve"
        echo "   - With UV: uv run uvicorn ai_research_framework.api.main:app --reload"
        echo "   - With Docker: docker-compose up --build"
        echo "3. Visit http://localhost:8000/docs for API documentation"
        echo "4. Run tests: make test or ./scripts/test.sh"
    fi
else
    print_error "Database initialization failed!"
    exit 1
fi

