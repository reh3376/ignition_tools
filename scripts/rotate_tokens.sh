#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to display help
show_help() {
    echo "Token Rotation Script"
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  -t, --token TYPE    Type of token to rotate (snyk, docker, all)"
    echo "  -h, --help         Show this help message"
    echo
    echo "Examples:"
    echo "  $0 -t snyk         Rotate Snyk token"
    echo "  $0 -t docker       Rotate Docker token"
    echo "  $0 -t all          Rotate all tokens"
}

# Parse command line arguments
TOKEN_TYPE=""
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--token)
            TOKEN_TYPE="$2"
            shift 2
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

# Check if token type is specified
if [ -z "$TOKEN_TYPE" ]; then
    echo "Error: Token type must be specified"
    show_help
    exit 1
fi

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

# Function to rotate Snyk token (disabled - requires enterprise subscription)
rotate_snyk_token() {
    echo "⚠️  Snyk token rotation is not available (requires enterprise subscription)"
    echo "   Using free security alternatives instead:"
    echo "   - Bandit for code security analysis"
    echo "   - Safety for known vulnerability scanning"
    echo "   - pip-audit for dependency vulnerability scanning"
    echo ""
    echo "   These tools are already configured in the security workflow."
    echo "   No token rotation needed for these free tools."
    echo ""
    echo "   If you need Snyk functionality in the future, you can:"
    echo "   1. Sign up for Snyk enterprise"
    echo "   2. Generate a Snyk token"
    echo "   3. Add it as SNYK_TOKEN GitHub secret"
    echo "   4. Re-enable Snyk in .github/workflows/security.yml"
}

# Function to rotate Docker token
rotate_docker_token() {
    echo "Rotating Docker token..."
    
    # Check if Docker is installed
    if ! command_exists docker; then
        echo "Docker is not installed. Please install Docker first."
        echo "Visit: https://docs.docker.com/get-docker/"
        exit 1
    fi

    # Get current token for backup
    CURRENT_TOKEN=$(gh secret get DOCKER_TOKEN 2>/dev/null)
    if [ -n "$CURRENT_TOKEN" ]; then
        echo "Backing up current Docker token..."
        echo "$CURRENT_TOKEN" > docker_token_backup.txt
        echo "Current token backed up to docker_token_backup.txt"
    fi

    # Run the Docker token setup script
    ./scripts/setup_docker_token.sh

    # Verify the new token
    echo "Verifying new Docker token..."
    gh workflow run verify-tokens.yml -f token_type=docker

    echo "Docker token rotation complete. Please verify the token works correctly."
    echo "If everything is working, you can revoke the old token at https://hub.docker.com/settings/security"
}

# Main script logic
case $TOKEN_TYPE in
    snyk)
        rotate_snyk_token
        ;;
    docker)
        rotate_docker_token
        ;;
    all)
        rotate_snyk_token
        rotate_docker_token
        ;;
    *)
        echo "Error: Invalid token type. Use 'snyk', 'docker', or 'all'"
        exit 1
        ;;
esac

echo "Token rotation process completed."
echo "Please review the verification workflow results in the GitHub Actions tab."
echo "Remember to revoke the old tokens if the new ones are working correctly." 