# Token Management Guide

This guide provides comprehensive information about managing security tokens used in the IGN Scripts project.

## Overview

The project uses security tokens for different purposes:

1. `DOCKER_TOKEN`: Used for Docker Hub authentication and image management
2. `GITHUB_TOKEN`: Automatically provided by GitHub Actions for repository access

**Note:** Snyk token has been removed as it requires an enterprise subscription. We use free security alternatives instead:
- **Bandit** - for code security analysis
- **Safety** - for known vulnerability scanning  
- **pip-audit** - for dependency vulnerability scanning

## Token Setup

### Security Scanning (Free Alternatives)

Instead of Snyk (which requires enterprise subscription), we use these free security tools:

#### Bandit
- Analyzes Python code for common security issues
- Automatically installed and run in CI/CD pipeline
- No configuration needed

#### Safety
- Checks Python dependencies for known vulnerabilities
- Uses PyUp.io database of known security vulnerabilities
- Automatically installed and run in CI/CD pipeline

#### pip-audit
- Official PyPA tool for scanning Python packages
- Checks for known vulnerabilities in dependencies
- More comprehensive than Safety for dependency scanning

### Docker Token

The Docker token is used for authenticating with Docker Hub and managing container images.

#### Automatic Setup

Use the provided script to set up the Docker token:

```bash
./scripts/setup_docker_token.sh
```

The script will:
1. Check for Docker installation
2. Guide you through Docker Hub authentication
3. Help create a new access token
4. Automatically add the token to GitHub repository secrets

#### Manual Setup

If you prefer to set up the token manually:

1. Visit [Docker Hub Security Settings](https://hub.docker.com/settings/security)
2. Click "New Access Token"
3. Configure the token:
   - Description: "GitHub Actions" (or your preferred name)
   - Expiration: Set to 1 year (recommended)
4. Copy the generated token
5. Go to your GitHub repository:
   - Navigate to Settings > Secrets and variables > Actions
   - Click "New repository secret"
   - Name: `DOCKER_TOKEN`
   - Value: Paste your Docker token
   - Click "Add secret"

## Token Verification

### Automated Verification

We provide a verification workflow to ensure tokens are working correctly:

1. Go to your GitHub repository
2. Click on the "Actions" tab
3. Select "Verify Token Access" from the workflows list
4. Click "Run workflow"
5. Select the main branch
6. Click "Run workflow"

The workflow will verify:
- Security tools are installed and working (Bandit, Safety, pip-audit)
- Docker token authentication and image access

### Manual Verification

#### Security Tools

```bash
# Test Bandit
bandit --version
bandit -r src/

# Test Safety
safety --version
safety check

# Test pip-audit
pip-audit --version
pip-audit
```

#### Docker Token

```bash
# Login to Docker Hub
echo $DOCKER_TOKEN | docker login -u your-username --password-stdin

# Try pulling an image
docker pull ghcr.io/reh3376/mcp:latest
```

## Token Rotation

### When to Rotate Tokens

Rotate your tokens in the following situations:
- Token expiration is approaching
- Token has been compromised
- Team member with token access leaves
- Regular security rotation (recommended every 90 days)

### Rotation Process

1. Create a new token following the setup instructions above
2. Update the token in GitHub repository secrets
3. Run the verification workflow to ensure the new token works
4. Revoke the old token from the respective service

## Security Best Practices

1. **Token Storage**
   - Never commit tokens to the repository
   - Use GitHub repository secrets for storage
   - Don't share tokens in logs or error messages

2. **Access Control**
   - Use tokens with minimum required permissions
   - Regularly audit token access
   - Rotate tokens periodically

3. **Monitoring**
   - Monitor token usage in GitHub Actions logs
   - Set up alerts for unusual token activity
   - Review security scan results regularly

4. **Documentation**
   - Keep this guide updated
   - Document any changes to token requirements
   - Maintain a list of services using each token

## Troubleshooting

### Common Issues

1. **Token Authentication Failed**
   - Verify token is correctly copied
   - Check token expiration
   - Ensure token has correct permissions

2. **Workflow Failures**
   - Check GitHub Actions logs
   - Verify token is properly set in repository secrets
   - Run the verification workflow

3. **Access Denied**
   - Verify token permissions
   - Check service-specific access logs
   - Ensure token hasn't been revoked

### Getting Help

If you encounter issues with token management:
1. Check the service-specific documentation
2. Review GitHub Actions logs
3. Contact the project maintainers
4. Open an issue in the repository

## Additional Resources

- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Snyk Documentation](https://docs.snyk.io/)
- [Docker Security Documentation](https://docs.docker.com/security/)
- [GitHub Actions Security](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions) 