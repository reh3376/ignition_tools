#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to display help
show_help() {
    echo "Test Runner Script"
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  -p, --python      Run Python tests"
    echo "  -n, --node        Run Node.js tests"
    echo "  -a, --all         Run all tests"
    echo "  -c, --coverage    Generate coverage report"
    echo "  -v, --verbose     Show verbose output"
    echo "  -h, --help        Show this help message"
    echo
    echo "Examples:"
    echo "  $0 -p             Run Python tests"
    echo "  $0 -a -c          Run all tests with coverage"
}

# Function to run Python tests
run_python_tests() {
    echo "Running Python tests..."
    
    # Check if Python virtual environment is activated
    if [ -z "$VIRTUAL_ENV" ]; then
        echo "Python virtual environment is not activated. Activating..."
        source .venv/bin/activate
    fi

    # Check if pytest is installed
    if ! command_exists pytest; then
        echo "pytest is not installed. Installing..."
        pip install pytest pytest-cov
    fi

    # Run tests with coverage if requested
    if [ "$GENERATE_COVERAGE" = true ]; then
        pytest tests/ --cov=src --cov-report=term-missing --cov-report=html
    else
        pytest tests/
    fi

    echo "Python tests completed."
}

# Function to run Node.js tests
run_node_tests() {
    echo "Running Node.js tests..."
    
    # Check if npm is installed
    if ! command_exists npm; then
        echo "npm is not installed. Please install npm first."
        exit 1
    fi

    # Run tests with coverage if requested
    if [ "$GENERATE_COVERAGE" = true ]; then
        npm test -- --coverage
    else
        npm test
    fi

    echo "Node.js tests completed."
}

# Parse command line arguments
RUN_PYTHON=false
RUN_NODE=false
GENERATE_COVERAGE=false
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--python)
            RUN_PYTHON=true
            shift
            ;;
        -n|--node)
            RUN_NODE=true
            shift
            ;;
        -a|--all)
            RUN_PYTHON=true
            RUN_NODE=true
            shift
            ;;
        -c|--coverage)
            GENERATE_COVERAGE=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# If no options specified, show help
if [ "$RUN_PYTHON" = false ] && [ "$RUN_NODE" = false ]; then
    show_help
    exit 1
fi

# Set pytest verbosity
if [ "$VERBOSE" = true ]; then
    export PYTEST_ADDOPTS="-v"
fi

# Main script logic
if [ "$RUN_PYTHON" = true ]; then
    run_python_tests
fi

if [ "$RUN_NODE" = true ]; then
    run_node_tests
fi

echo "Test execution completed."
if [ "$GENERATE_COVERAGE" = true ]; then
    echo "Coverage reports have been generated."
    echo "Python coverage report: htmlcov/index.html"
    echo "Node.js coverage report: coverage/lcov-report/index.html"
fi 