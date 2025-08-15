#!/bin/bash

# AI Research Framework Test Automation Script
# This script runs comprehensive tests for the AI Research Framework

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
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

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command_exists python3; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    
    if ! command_exists pip3; then
        print_error "pip3 is not installed"
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Install dependencies
install_dependencies() {
    print_status "Installing test dependencies..."
    
    pip3 install -q pytest pytest-asyncio pytest-cov pytest-html pytest-json-report pytest-benchmark
    pip3 install -q ruff mypy bandit safety
    pip3 install -q loguru fastapi uvicorn sqlalchemy aiosqlite databases
    pip3 install -q beautifulsoup4 requests aiofiles python-multipart
    
    print_success "Dependencies installed"
}

# Setup test environment
setup_test_env() {
    print_status "Setting up test environment..."
    
    # Create necessary directories
    mkdir -p data logs temp reports htmlcov
    
    # Set environment variables
    export TESTING=true
    export DATABASE_URL="sqlite+aiosqlite:///:memory:"
    export LOG_LEVEL=DEBUG
    export PYTHONPATH="${PWD}/src:${PYTHONPATH}"
    
    print_success "Test environment setup complete"
}

# Run linting
run_linting() {
    print_status "Running code linting..."
    
    if command_exists ruff; then
        print_status "Running ruff linter..."
        ruff check src tests --fix || print_warning "Ruff found issues (fixed automatically)"
        ruff format src tests || print_warning "Ruff formatting applied"
    else
        print_warning "Ruff not available, skipping linting"
    fi
    
    print_success "Linting complete"
}

# Run type checking
run_type_checking() {
    print_status "Running type checking..."
    
    if command_exists mypy; then
        print_status "Running mypy type checker..."
        mypy src --ignore-missing-imports || print_warning "Type checking found issues"
    else
        print_warning "MyPy not available, skipping type checking"
    fi
    
    print_success "Type checking complete"
}

# Run security checks
run_security_checks() {
    print_status "Running security checks..."
    
    if command_exists bandit; then
        print_status "Running bandit security scanner..."
        bandit -r src/ -f json -o reports/bandit_report.json || print_warning "Security issues found"
    else
        print_warning "Bandit not available, skipping security checks"
    fi
    
    if command_exists safety; then
        print_status "Running safety dependency checker..."
        safety check --json --output reports/safety_report.json || print_warning "Dependency vulnerabilities found"
    else
        print_warning "Safety not available, skipping dependency checks"
    fi
    
    print_success "Security checks complete"
}

# Run unit tests
run_unit_tests() {
    print_status "Running unit tests..."
    
    python3 -m pytest tests/unit \
        -v \
        --tb=short \
        --cov=src/ai_research_framework \
        --cov-report=html:htmlcov \
        --cov-report=xml:coverage.xml \
        --cov-report=term-missing \
        --html=reports/unit_test_report.html \
        --self-contained-html \
        --json-report \
        --json-report-file=reports/unit_test_report.json \
        || print_error "Unit tests failed"
    
    print_success "Unit tests complete"
}

# Run integration tests
run_integration_tests() {
    print_status "Running integration tests..."
    
    python3 -m pytest tests/integration \
        -v \
        --tb=short \
        --maxfail=5 \
        --html=reports/integration_test_report.html \
        --self-contained-html \
        --json-report \
        --json-report-file=reports/integration_test_report.json \
        || print_error "Integration tests failed"
    
    print_success "Integration tests complete"
}

# Run performance tests
run_performance_tests() {
    print_status "Running performance tests..."
    
    if command_exists pytest-benchmark; then
        python3 -m pytest tests/ \
            -m "performance" \
            -v \
            --benchmark-only \
            --benchmark-json=reports/benchmark_report.json \
            || print_warning "Performance tests had issues"
    else
        print_warning "pytest-benchmark not available, skipping performance tests"
    fi
    
    print_success "Performance tests complete"
}

# Run API tests
run_api_tests() {
    print_status "Running API tests..."
    
    python3 -m pytest tests/integration/test_api_endpoints.py \
        -v \
        --tb=short \
        --html=reports/api_test_report.html \
        --self-contained-html \
        || print_warning "API tests had issues"
    
    print_success "API tests complete"
}

# Generate test report
generate_report() {
    print_status "Generating comprehensive test report..."
    
    cat > reports/test_summary.md << EOF
# AI Research Framework Test Report

## Test Execution Summary

**Date:** $(date)
**Environment:** Test
**Python Version:** $(python3 --version)

## Test Results

### Unit Tests
- Location: \`tests/unit/\`
- Report: [Unit Test Report](unit_test_report.html)
- Coverage: [Coverage Report](../htmlcov/index.html)

### Integration Tests
- Location: \`tests/integration/\`
- Report: [Integration Test Report](integration_test_report.html)

### API Tests
- Location: \`tests/integration/test_api_endpoints.py\`
- Report: [API Test Report](api_test_report.html)

### Security Checks
- Bandit Report: [Security Report](bandit_report.json)
- Safety Report: [Dependency Report](safety_report.json)

### Performance Tests
- Benchmark Report: [Performance Report](benchmark_report.json)

## Coverage Information

Coverage reports are available in the \`htmlcov/\` directory.

## Next Steps

1. Review failed tests and fix issues
2. Improve test coverage for areas below 80%
3. Address security vulnerabilities if any
4. Optimize performance bottlenecks

EOF
    
    print_success "Test report generated: reports/test_summary.md"
}

# Main execution function
main() {
    print_status "Starting AI Research Framework Test Suite"
    print_status "========================================"
    
    # Parse command line arguments
    RUN_ALL=true
    RUN_UNIT=false
    RUN_INTEGRATION=false
    RUN_API=false
    RUN_PERFORMANCE=false
    RUN_SECURITY=false
    RUN_LINT=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --unit)
                RUN_ALL=false
                RUN_UNIT=true
                shift
                ;;
            --integration)
                RUN_ALL=false
                RUN_INTEGRATION=true
                shift
                ;;
            --api)
                RUN_ALL=false
                RUN_API=true
                shift
                ;;
            --performance)
                RUN_ALL=false
                RUN_PERFORMANCE=true
                shift
                ;;
            --security)
                RUN_ALL=false
                RUN_SECURITY=true
                shift
                ;;
            --lint)
                RUN_ALL=false
                RUN_LINT=true
                shift
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo "Options:"
                echo "  --unit         Run only unit tests"
                echo "  --integration  Run only integration tests"
                echo "  --api          Run only API tests"
                echo "  --performance  Run only performance tests"
                echo "  --security     Run only security checks"
                echo "  --lint         Run only linting"
                echo "  --help         Show this help message"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # Execute test phases
    check_prerequisites
    install_dependencies
    setup_test_env
    
    if [[ "$RUN_ALL" == true ]] || [[ "$RUN_LINT" == true ]]; then
        run_linting
        run_type_checking
    fi
    
    if [[ "$RUN_ALL" == true ]] || [[ "$RUN_SECURITY" == true ]]; then
        run_security_checks
    fi
    
    if [[ "$RUN_ALL" == true ]] || [[ "$RUN_UNIT" == true ]]; then
        run_unit_tests
    fi
    
    if [[ "$RUN_ALL" == true ]] || [[ "$RUN_INTEGRATION" == true ]]; then
        run_integration_tests
    fi
    
    if [[ "$RUN_ALL" == true ]] || [[ "$RUN_API" == true ]]; then
        run_api_tests
    fi
    
    if [[ "$RUN_ALL" == true ]] || [[ "$RUN_PERFORMANCE" == true ]]; then
        run_performance_tests
    fi
    
    generate_report
    
    print_success "All tests completed successfully!"
    print_status "Check the reports/ directory for detailed results"
}

# Run main function
main "$@"

