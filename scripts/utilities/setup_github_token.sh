#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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

# Check if .env file exists
if [ ! -f .env ]; then
    print_warning "Creating .env file..."
    touch .env
fi

# Prompt for GitHub username
read -p "Enter your GitHub username: " github_username

# Prompt for GitHub token
read -sp "Enter your GitHub Personal Access Token: " github_token
echo

# Add to .env file
echo "GITHUB_TOKEN=$github_token" >> .env
echo "GITHUB_USERNAME=$github_username" >> .env

# Source the .env file
source .env

print_status "GitHub token has been added to .env file"
print_status "You can now run ./scripts/utilities/start_services.sh" 