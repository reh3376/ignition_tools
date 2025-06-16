#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to display help
show_help() {
    echo "Development Environment Setup Script"
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  -p, --python      Setup Python environment"
    echo "  -n, --node        Setup Node.js environment"
    echo "  -d, --docker      Setup Docker environment"
    echo "  -a, --all         Setup all environments"
    echo "  -h, --help        Show this help message"
    echo
    echo "Examples:"
    echo "  $0 -p             Setup Python environment"
    echo "  $0 -a             Setup all environments"
}

# Function to setup Python environment
setup_python_env() {
    echo "Setting up Python environment..."
    
    # Check if Python is installed
    if ! command_exists python3; then
        echo "Python 3 is not installed. Please install Python 3 first."
        echo "Visit: https://www.python.org/downloads/"
        exit 1
    fi

    # Check if uv is installed
    if ! command_exists uv; then
        echo "Installing uv..."
        pip install uv
    fi

    # Create virtual environment
    echo "Creating virtual environment..."
    uv venv

    # Activate virtual environment
    echo "Activating virtual environment..."
    source .venv/bin/activate

    # Install dependencies
    echo "Installing Python dependencies..."
    uv pip install -r requirements.txt

    # Install development dependencies
    echo "Installing development dependencies..."
    uv pip install -r requirements-dev.txt

    # Install pre-commit hooks
    echo "Installing pre-commit hooks..."
    pre-commit install

    echo "Python environment setup complete."
}

# Function to setup Node.js environment
setup_node_env() {
    echo "Setting up Node.js environment..."
    
    # Check if Node.js is installed
    if ! command_exists node; then
        echo "Node.js is not installed. Please install Node.js first."
        echo "Visit: https://nodejs.org/"
        exit 1
    fi

    # Check if npm is installed
    if ! command_exists npm; then
        echo "npm is not installed. Please install npm first."
        exit 1
    fi

    # Install dependencies
    echo "Installing Node.js dependencies..."
    npm install

    # Install development dependencies
    echo "Installing development dependencies..."
    npm install --save-dev

    echo "Node.js environment setup complete."
}

# Function to setup Docker environment
setup_docker_env() {
    echo "Setting up Docker environment..."
    
    # Check if Docker is installed
    if ! command_exists docker; then
        echo "Docker is not installed. Please install Docker first."
        echo "Visit: https://docs.docker.com/get-docker/"
        exit 1
    fi

    # Check if Docker Compose is installed
    if ! command_exists docker-compose; then
        echo "Docker Compose is not installed. Please install Docker Compose first."
        echo "Visit: https://docs.docker.com/compose/install/"
        exit 1
    fi

    # Build Docker images
    echo "Building Docker images..."
    docker-compose build

    # Create necessary directories
    echo "Creating necessary directories..."
    mkdir -p data/neo4j
    mkdir -p data/postgres
    mkdir -p logs

    echo "Docker environment setup complete."
}

# Parse command line arguments
SETUP_PYTHON=false
SETUP_NODE=false
SETUP_DOCKER=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--python)
            SETUP_PYTHON=true
            shift
            ;;
        -n|--node)
            SETUP_NODE=true
            shift
            ;;
        -d|--docker)
            SETUP_DOCKER=true
            shift
            ;;
        -a|--all)
            SETUP_PYTHON=true
            SETUP_NODE=true
            SETUP_DOCKER=true
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
if [ "$SETUP_PYTHON" = false ] && [ "$SETUP_NODE" = false ] && [ "$SETUP_DOCKER" = false ]; then
    show_help
    exit 1
fi

# Main script logic
if [ "$SETUP_PYTHON" = true ]; then
    setup_python_env
fi

if [ "$SETUP_NODE" = true ]; then
    setup_node_env
fi

if [ "$SETUP_DOCKER" = true ]; then
    setup_docker_env
fi

echo "Development environment setup completed."
echo "Please review the setup and verify all components are working correctly." 