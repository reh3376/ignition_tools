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

# Function to setup repository
setup_repo() {
    local repo_name=$1
    local repo_path=$2

    echo "Setting up repository: $repo_name"
    cd "$repo_path" || exit 1

    # Initialize git if not already initialized
    if [ ! -d .git ]; then
        git init
        git add .
        git commit -m "Initial commit"
    fi

    # Create repository on GitHub if it doesn't exist
    if ! gh repo view "reh3376/$repo_name" >/dev/null 2>&1; then
        gh repo create "reh3376/$repo_name" --public --source=. --remote=origin
    fi

    # Enable GitHub Pages
    gh repo edit "reh3376/$repo_name" --enable-pages --pages-source=gh-pages

    # Set up branch protection rules
    gh api repos/reh3376/$repo_name/branches/main/protection \
        -X PUT \
        -H "Accept: application/vnd.github.v3+json" \
        -f required_status_checks='{"strict":true,"contexts":["test","lint"]}' \
        -f enforce_admins=true \
        -f required_pull_request_reviews='{"dismissal_restrictions":{},"dismiss_stale_reviews":true,"require_code_owner_reviews":true,"required_approving_review_count":1}' \
        -f restrictions=null

    # Set up repository secrets
    if [ -n "$DOCKER_TOKEN" ]; then
        gh secret set DOCKER_TOKEN -b"$DOCKER_TOKEN" -R "reh3376/$repo_name"
    fi

    if [ -n "$CODECOV_TOKEN" ]; then
        gh secret set CODECOV_TOKEN -b"$CODECOV_TOKEN" -R "reh3376/$repo_name"
    fi

    echo "Repository setup complete: $repo_name"
}

# Main script
echo "Setting up GitHub repositories..."

# Setup MCP repository
setup_repo "mcp" "../mcp"

# Setup MCP Tools repository
setup_repo "mcp-tools" "../mcp-tools"

echo "All repositories have been set up successfully!" 