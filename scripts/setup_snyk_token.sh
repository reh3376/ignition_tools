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

# Check if Snyk CLI is installed
if ! command_exists snyk; then
    echo "Snyk CLI is not installed. Installing..."
    npm install -g snyk
fi

# Authenticate with Snyk
echo "Please authenticate with Snyk:"
snyk auth

# Get the Snyk token
SNYK_TOKEN=$(snyk config get api)

if [ -z "$SNYK_TOKEN" ]; then
    echo "Failed to get Snyk token. Please make sure you're authenticated with Snyk."
    exit 1
fi

# Add the token to GitHub repository secrets
echo "Adding Snyk token to GitHub repository secrets..."
gh secret set SNYK_TOKEN -b"$SNYK_TOKEN"

echo "Snyk token has been added to GitHub repository secrets."
echo "You can verify this in your repository settings under Settings > Secrets and variables > Actions" 