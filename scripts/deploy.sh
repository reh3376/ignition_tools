#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to display help
show_help() {
    echo "Deployment Script"
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  -e, --env ENV      Deployment environment (dev, staging, prod)"
    echo "  -s, --service SVC  Service to deploy (mcp, mcp-tools, all)"
    echo "  -v, --version VER  Version to deploy (default: latest)"
    echo "  -f, --force        Force deployment without confirmation"
    echo "  -h, --help         Show this help message"
    echo
    echo "Examples:"
    echo "  $0 -e dev -s mcp           Deploy MCP to dev environment"
    echo "  $0 -e prod -s all -v 1.0.0 Deploy all services to prod with version 1.0.0"
}

# Function to validate environment
validate_environment() {
    local env=$1
    case $env in
        dev|staging|prod)
            return 0
            ;;
        *)
            echo "Error: Invalid environment. Use 'dev', 'staging', or 'prod'"
            return 1
            ;;
    esac
}

# Function to validate service
validate_service() {
    local svc=$1
    case $svc in
        mcp|mcp-tools|all)
            return 0
            ;;
        *)
            echo "Error: Invalid service. Use 'mcp', 'mcp-tools', or 'all'"
            return 1
            ;;
    esac
}

# Function to check prerequisites
check_prerequisites() {
    # Check if Docker is installed
    if ! command_exists docker; then
        echo "Error: Docker is not installed"
        exit 1
    fi

    # Check if Docker Compose is installed
    if ! command_exists docker-compose; then
        echo "Error: Docker Compose is not installed"
        exit 1
    fi

    # Check if GitHub CLI is installed
    if ! command_exists gh; then
        echo "Error: GitHub CLI is not installed"
        exit 1
    fi

    # Check if user is logged in to GitHub
    if ! gh auth status >/dev/null 2>&1; then
        echo "Error: Not logged in to GitHub"
        echo "Please run: gh auth login"
        exit 1
    fi
}

# Function to build and push Docker images
build_and_push_images() {
    local service=$1
    local version=$2
    local env=$3

    echo "Building and pushing $service:$version for $env environment..."

    # Build the image
    docker build -t ghcr.io/reh3376/$service:$version \
        -t ghcr.io/reh3376/$service:latest \
        -f $service/Dockerfile .

    # Push the image
    docker push ghcr.io/reh3376/$service:$version
    docker push ghcr.io/reh3376/$service:latest

    echo "$service:$version has been built and pushed successfully."
}

# Function to deploy service
deploy_service() {
    local service=$1
    local version=$2
    local env=$3

    echo "Deploying $service:$version to $env environment..."

    # Create environment-specific compose file
    local compose_file="docker-compose.$env.yml"
    if [ ! -f "$compose_file" ]; then
        echo "Error: $compose_file not found"
        exit 1
    fi

    # Deploy using Docker Compose
    docker-compose -f $compose_file up -d $service

    echo "$service has been deployed successfully."
}

# Parse command line arguments
ENVIRONMENT=""
SERVICE=""
VERSION="latest"
FORCE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--env)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -s|--service)
            SERVICE="$2"
            shift 2
            ;;
        -v|--version)
            VERSION="$2"
            shift 2
            ;;
        -f|--force)
            FORCE=true
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

# Validate required arguments
if [ -z "$ENVIRONMENT" ] || [ -z "$SERVICE" ]; then
    echo "Error: Environment and service must be specified"
    show_help
    exit 1
fi

# Validate environment and service
if ! validate_environment "$ENVIRONMENT"; then
    exit 1
fi

if ! validate_service "$SERVICE"; then
    exit 1
fi

# Check prerequisites
check_prerequisites

# Confirm deployment
if [ "$FORCE" = false ]; then
    echo "About to deploy:"
    echo "Environment: $ENVIRONMENT"
    echo "Service(s): $SERVICE"
    echo "Version: $VERSION"
    read -p "Do you want to continue? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Deployment cancelled"
        exit 1
    fi
fi

# Main deployment logic
if [ "$SERVICE" = "all" ]; then
    # Deploy all services
    build_and_push_images "mcp" "$VERSION" "$ENVIRONMENT"
    build_and_push_images "mcp-tools" "$VERSION" "$ENVIRONMENT"
    deploy_service "mcp" "$VERSION" "$ENVIRONMENT"
    deploy_service "mcp-tools" "$VERSION" "$ENVIRONMENT"
else
    # Deploy single service
    build_and_push_images "$SERVICE" "$VERSION" "$ENVIRONMENT"
    deploy_service "$SERVICE" "$VERSION" "$ENVIRONMENT"
fi

echo "Deployment completed successfully."
echo "Please verify the services are running correctly in the $ENVIRONMENT environment." 