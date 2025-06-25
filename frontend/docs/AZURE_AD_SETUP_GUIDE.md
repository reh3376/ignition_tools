# Azure AD Application Registration Guide for Whiskey House Tenant

## Overview
This guide walks through registering the IGN Scripts React frontend application in Azure Active Directory for the Whiskey House tenant (whiskeyhouse.com domain) to enable Single Sign-On (SSO) authentication.

## Prerequisites

### Required Access
- **Azure AD Administrator** access to the Whiskey House tenant
- Permissions to create app registrations in Azure AD
- Access to the Azure Portal (https://portal.azure.com)

### Application Details
- **Application Name**: IGN Scripts - Industrial Automation Platform
- **Application Type**: Single-page application (SPA)
- **Supported Account Types**: Accounts in this organizational directory only (Whiskey House only)
- **Domain**: whiskeyhouse.com

## Step-by-Step Registration Process

### Step 1: Access Azure Portal
1. Navigate to https://portal.azure.com
2. Sign in with your Whiskey House administrator account (`admin@whiskeyhouse.com`)
3. Navigate to **Azure Active Directory** from the left menu
4. Select **App registrations** from the left sidebar

### Step 2: Create New App Registration
1. Click **+ New registration** button
2. Fill in the application details:

   **Basic Information:**
   - **Name**: `IGN Scripts - Industrial Automation Platform`
   - **Supported account types**: Select "Accounts in this organizational directory only (Whiskey House only - Single tenant)"
   - **Redirect URI**:
     - Type: Single-page application (SPA)
     - URI: `http://localhost:5173/auth/callback` (for development)

3. Click **Register** to create the application

### Step 3: Configure Application Settings

#### A. Note the Application Details
After registration, you'll see the **Overview** page. **Record these values:**

```
Application (client) ID: [Copy this GUID]
Directory (tenant) ID: [Copy this GUID]
Object ID: [Copy this GUID]
```

#### B. Configure Authentication
1. Go to **Authentication** in the left sidebar
2. Under **Platform configurations**, verify the SPA configuration
3. Add additional redirect URIs:
   - Development: `http://localhost:5173/auth/callback`
   - Production: `https://your-production-domain.com/auth/callback`
   - Testing: `https://your-staging-domain.com/auth/callback`

4. Under **Advanced settings**:
   - ✅ Enable **Access tokens** (used for implicit flows)
   - ✅ Enable **ID tokens** (used for implicit and hybrid flows)
   - ✅ Enable **Allow public client flows** (for mobile and desktop apps)

#### C. Configure API Permissions
1. Go to **API permissions** in the left sidebar
2. Click **+ Add a permission**
3. Select **Microsoft Graph**
4. Choose **Delegated permissions**
5. Add the following permissions:
   - ✅ `openid` (Sign users in)
   - ✅ `profile` (View users' basic profile)
   - ✅ `email` (View users' email address)
   - ✅ `User.Read` (Sign in and read user profile)

6. Click **Add permissions**
7. Click **Grant admin consent for Whiskey House** (requires admin privileges)

#### D. Configure Token Configuration (Optional)
1. Go to **Token configuration** in the left sidebar
2. Click **+ Add optional claim**
3. Select **ID** token type
4. Add claims if needed:
   - `email` (if not already included)
   - `family_name` and `given_name` (for full name)
   - `preferred_username` (for display purposes)

#### E. Configure Branding (Optional)
1. Go to **Branding** in the left sidebar
2. Add application details:
   - **Home page URL**: `https://your-production-domain.com`
   - **Terms of service URL**: `https://your-production-domain.com/terms`
   - **Privacy statement URL**: `https://your-production-domain.com/privacy`
   - **Logo**: Upload IGN Scripts logo (240x240px PNG)

### Step 4: Configure Domain Restrictions

#### A. Set Up Conditional Access (Recommended)
1. Navigate to **Azure AD** > **Security** > **Conditional Access**
2. Create a new policy for IGN Scripts:
   - **Name**: `IGN Scripts - Whiskey House Domain Only`
   - **Users**: All users
   - **Cloud apps**: Select "IGN Scripts - Industrial Automation Platform"
   - **Conditions**:
     - **Locations**: Exclude trusted locations if needed
     - **Device platforms**: Configure as needed
   - **Grant**: Grant access, require MFA if desired
   - **Session**: Configure session controls if needed

#### B. Configure User Assignment (Optional)
1. Go back to your app registration
2. Navigate to **Enterprise applications** in Azure AD
3. Find "IGN Scripts - Industrial Automation Platform"
4. Go to **Properties**
5. Set **User assignment required?** to **Yes** if you want to control access
6. Go to **Users and groups** to assign specific users/groups

### Step 5: Test Configuration

#### A. Verify App Registration
1. Go to **App registrations** > **IGN Scripts - Industrial Automation Platform**
2. Check **Overview** tab for correct configuration
3. Verify **Authentication** settings match requirements
4. Confirm **API permissions** are granted

#### B. Test Authentication Flow
1. Use the Application (client) ID in your frontend configuration
2. Test the login flow with a Whiskey House user account
3. Verify tokens are received correctly
4. Check user claims and permissions

## Configuration Values for Frontend

After completing the registration, update your frontend `.env` file with these values:

```env
# Whiskey House Microsoft SSO Configuration
VITE_WHISKEY_HOUSE_TENANT_ID=whiskeyhouse
VITE_WHISKEY_HOUSE_CLIENT_ID=[Your Application (client) ID from Step 3A]
VITE_WHISKEY_HOUSE_AUTHORITY=https://login.microsoftonline.com/whiskeyhouse.com

# Authentication Configuration
VITE_AUTH_REDIRECT_URI=http://localhost:5173/auth/callback

# Optional: Use tenant GUID instead of domain
# VITE_WHISKEY_HOUSE_AUTHORITY=https://login.microsoftonline.com/[Your Directory (tenant) ID]
```

## Security Considerations

### Required Security Settings
1. **Single Tenant Only**: Ensure only Whiskey House accounts can authenticate
2. **HTTPS in Production**: All production redirect URIs must use HTTPS
3. **Domain Validation**: Application validates `@whiskeyhouse.com` email domain
4. **Token Validation**: Implement proper token validation and refresh logic

### Recommended Security Enhancements
1. **Multi-Factor Authentication**: Enable MFA requirement in Conditional Access
2. **Device Compliance**: Require compliant or hybrid Azure AD joined devices
3. **Location-Based Access**: Restrict access from untrusted locations
4. **Session Management**: Configure appropriate session timeouts

## Troubleshooting Common Issues

### Issue: "AADSTS50011: The reply URL specified in the request does not match"
**Solution**: Verify redirect URIs in Authentication settings match exactly

### Issue: "AADSTS65001: The user or administrator has not consented"
**Solution**: Grant admin consent for required permissions

### Issue: "AADSTS50020: User account from identity provider does not exist"
**Solution**: Ensure user exists in Whiskey House tenant and domain is correct

### Issue: "AADSTS700016: Application not found in the directory"
**Solution**: Verify Application (client) ID is correct and app is in correct tenant

## Next Steps After Registration

1. **Update Frontend Configuration**: Add the Application (client) ID to your `.env` file
2. **Test Development Environment**: Verify SSO works with localhost
3. **Configure Production URLs**: Add production redirect URIs before deployment
4. **Set Up Monitoring**: Configure Azure AD sign-in logs monitoring
5. **Document User Onboarding**: Create user guide for Whiskey House employees

## Support and Documentation

- **Azure AD Documentation**: https://docs.microsoft.com/en-us/azure/active-directory/
- **Microsoft Identity Platform**: https://docs.microsoft.com/en-us/azure/active-directory/develop/
- **MSAL.js Documentation**: https://docs.microsoft.com/en-us/azure/active-directory/develop/msal-js-initializing-client-applications

## Contact Information

For assistance with Azure AD configuration:
- **IT Administrator**: Contact your Whiskey House IT department
- **Microsoft Support**: Available through Azure Portal if you have a support plan
- **Application Developer**: Contact the IGN Scripts development team

---

**Important**: Keep the Application (client) ID and any secrets secure. Do not commit these values to version control.
