#!/bin/bash

# Start Services Script for IGN Scripts
# This script ensures all required services are running and initialized

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Docker paths
DOCKER="/Applications/Docker.app/Contents/Resources/bin/docker"
DOCKER_COMPOSE="$DOCKER compose"  # New Docker Compose V2 syntax

# Function to print status messages
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Load environment variables
if [ -f .env ]; then
    source .env
else
    print_error ".env file not found. Please run ./scripts/utilities/setup_github_token.sh first."
    exit 1
fi

# Check if Docker is running
if ! $DOCKER info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check GitHub authentication
if [ -z "$GITHUB_TOKEN" ] || [ -z "$GITHUB_USERNAME" ]; then
    print_warning "GitHub credentials not found. Please run ./scripts/utilities/setup_github_token.sh first."
    exit 1
fi

# Login to GitHub Container Registry
print_status "Logging in to GitHub Container Registry..."
if ! echo "$GITHUB_TOKEN" | $DOCKER login ghcr.io -u "$GITHUB_USERNAME" --password-stdin; then
    print_error "Failed to login to GitHub Container Registry"
    exit 1
fi

# Pull required images first
print_status "Pulling required Docker images..."
$DOCKER pull neo4j:5.15-community

# Check if MCP images are accessible
print_status "Checking MCP image access..."
if ! $DOCKER pull ghcr.io/github-tools/mcp:latest 2>/dev/null; then
    print_warning "MCP image not accessible. Please ensure you have access to the MCP repository."
    print_warning "You may need to:"
    print_warning "1. Request access to the MCP repository"
    print_warning "2. Ensure your GitHub token has the correct permissions"
    print_warning "3. Check if the repository name is correct"
    exit 1
fi

if ! $DOCKER pull ghcr.io/github-tools/mcp-tools:latest 2>/dev/null; then
    print_warning "MCP Tools image not accessible. Please ensure you have access to the MCP Tools repository."
    print_warning "You may need to:"
    print_warning "1. Request access to the MCP Tools repository"
    print_warning "2. Ensure your GitHub token has the correct permissions"
    print_warning "3. Check if the repository name is correct"
    exit 1
fi

# Start Neo4j service first
print_status "Starting Neo4j service..."
if ! $DOCKER_COMPOSE up -d neo4j; then
    print_error "Failed to start Neo4j service"
    exit 1
fi

# Wait for Neo4j to be ready
print_status "Waiting for Neo4j to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:7474 > /dev/null; then
        print_status "Neo4j is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "Neo4j failed to start within timeout"
        exit 1
    fi
    sleep 1
done

# Start MCP services
print_status "Starting MCP services..."
if ! $DOCKER_COMPOSE up -d mcp mcp-tools; then
    print_error "Failed to start MCP services"
    exit 1
fi

# Wait for MCP services to be ready
print_status "Waiting for MCP services to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8080/health > /dev/null && \
       curl -s http://localhost:8082/health > /dev/null; then
        print_status "MCP services are ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "MCP services failed to start within timeout"
        exit 1
    fi
    sleep 1
done

# Run the startup script
print_status "Initializing clients..."
if ! python3 scripts/utilities/startup.py; then
    print_error "Failed to initialize clients"
    exit 1
fi

print_status "All services are running and initialized successfully!"
print_status "Neo4j Browser: http://localhost:7474"
print_status "MCP API: http://localhost:8080"
print_status "MCP Tools API: http://localhost:8082" 