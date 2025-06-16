#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if gh CLI is installed
if ! command_exists gh; then
    echo "GitHub CLI (gh) is not installed. Please install it first."
    echo "Visit: https://cli.github.com/manual/installation"
    exit 1
fi

# Check if user is logged in to GitHub
if ! gh auth status >/dev/null 2>&1; then
    echo "Please log in to GitHub first:"
    gh auth login
fi

# Check if Docker is installed
if ! command_exists docker; then
    echo "Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if user is logged in to Docker Hub
if ! docker info | grep -q "Username"; then
    echo "Please log in to Docker Hub first:"
    read -p "Docker Hub Username: " DOCKER_USERNAME
    read -sp "Docker Hub Password: " DOCKER_PASSWORD
    echo
    echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
fi

# Create Docker access token
echo "Creating Docker access token..."
echo "Please visit: https://hub.docker.com/settings/security"
echo "Click 'New Access Token' and follow these steps:"
echo "1. Enter a description (e.g., 'GitHub Actions')"
echo "2. Set an expiration date (recommended: 1 year)"
echo "3. Click 'Generate'"
echo "4. Copy the generated token"
read -sp "Paste your Docker access token here: " DOCKER_TOKEN
echo

if [ -z "$DOCKER_TOKEN" ]; then
    echo "No token provided. Please try again."
    exit 1
fi

# Add the token to GitHub repository secrets
echo "Adding Docker token to GitHub repository secrets..."
gh secret set DOCKER_TOKEN -b"$DOCKER_TOKEN"

echo "Docker token has been added to GitHub repository secrets."
echo "You can verify this in your repository settings under Settings > Secrets and variables > Actions" 