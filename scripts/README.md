# Scripts Directory

This directory contains utility scripts for managing the MCP and MCP Tools services.

## Available Scripts

### Token Management

- `rotate_tokens.sh`: Script for rotating Snyk and Docker tokens
  ```bash
  # Rotate Snyk token
  ./rotate_tokens.sh -t snyk

  # Rotate Docker token
  ./rotate_tokens.sh -t docker

  # Rotate all tokens
  ./rotate_tokens.sh -t all
  ```

- `setup_snyk_token.sh`: Script for setting up Snyk token
  ```bash
  ./setup_snyk_token.sh
  ```

- `setup_docker_token.sh`: Script for setting up Docker token
  ```bash
  ./setup_docker_token.sh
  ```

### Development

- `setup_dev_env.sh`: Script for setting up development environment
  ```bash
  ./setup_dev_env.sh
  ```

- `run_tests.sh`: Script for running tests
  ```bash
  ./run_tests.sh
  ```

### Deployment

- `deploy.sh`: Script for deploying services
  ```bash
  ./deploy.sh
  ```

## Usage

1. Make sure the scripts are executable:
   ```bash
   chmod +x scripts/*.sh
   ```

2. Run the desired script with appropriate arguments:
   ```bash
   ./scripts/rotate_tokens.sh -t snyk
   ```

## Requirements

- Bash shell
- GitHub CLI (`gh`)
- Docker (for Docker-related scripts)
- Snyk CLI (for Snyk-related scripts)

## Security Notes

- Token backup files are created during rotation for safety
- Old tokens should be revoked after successful rotation
- Backup files should be securely deleted after verification
- Scripts require appropriate permissions to run

## Troubleshooting

If you encounter issues:

1. Check if all required tools are installed
2. Verify you have necessary permissions
3. Check the GitHub Actions tab for verification results
4. Review the token management documentation in `docs/security/token-management.md` 