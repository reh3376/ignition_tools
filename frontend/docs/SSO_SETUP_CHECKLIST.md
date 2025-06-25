# Whiskey House SSO Setup Checklist

## Pre-Registration Checklist

### ✅ Prerequisites Completed
- [ ] **Azure AD Administrator Access**: Confirm you have admin rights to the Whiskey House tenant
- [ ] **Domain Verification**: Confirm whiskeyhouse.com domain is verified in Azure AD
- [ ] **Portal Access**: Can access https://portal.azure.com with admin account
- [ ] **Development Environment**: Frontend development environment is set up

## Azure AD App Registration Process

### ✅ Step 1: Create App Registration
- [ ] Navigate to Azure Portal > Azure Active Directory > App registrations
- [ ] Click "+ New registration"
- [ ] Enter application name: `IGN Scripts - Industrial Automation Platform`
- [ ] Select "Accounts in this organizational directory only (Whiskey House only)"
- [ ] Set redirect URI type to "Single-page application (SPA)"
- [ ] Set redirect URI to: `http://localhost:5173/auth/callback`
- [ ] Click "Register"

### ✅ Step 2: Record Application Details
Copy these values from the Overview page:
- [ ] **Application (client) ID**: `_________________________`
- [ ] **Directory (tenant) ID**: `_________________________`
- [ ] **Object ID**: `_________________________`

### ✅ Step 3: Configure Authentication
- [ ] Go to Authentication > Platform configurations
- [ ] Verify SPA configuration is correct
- [ ] Add production redirect URI (when ready): `https://your-domain.com/auth/callback`
- [ ] Enable "Access tokens" under Advanced settings
- [ ] Enable "ID tokens" under Advanced settings

### ✅ Step 4: Set API Permissions
- [ ] Go to API permissions
- [ ] Verify these permissions are present:
  - [ ] `openid` (Sign users in)
  - [ ] `profile` (View users' basic profile)
  - [ ] `email` (View users' email address)
  - [ ] `User.Read` (Sign in and read user profile)
- [ ] Click "Grant admin consent for Whiskey House"
- [ ] Verify consent status shows "Granted for Whiskey House"

### ✅ Step 5: Configure Domain Restrictions (Optional but Recommended)
- [ ] Set up Conditional Access policy for IGN Scripts
- [ ] Configure user assignment if needed
- [ ] Test with a Whiskey House user account

## Frontend Configuration

### ✅ Step 6: Update Environment Variables
Create `.env` file in frontend directory with:

```env
# From Step 2 above - replace with your actual values
VITE_WHISKEY_HOUSE_TENANT_ID=whiskeyhouse
VITE_WHISKEY_HOUSE_CLIENT_ID=[Your Application (client) ID]
VITE_WHISKEY_HOUSE_AUTHORITY=https://login.microsoftonline.com/whiskeyhouse.com
VITE_AUTH_REDIRECT_URI=http://localhost:5173/auth/callback
```

### ✅ Step 7: Install Dependencies
- [ ] Run `npm install @azure/msal-browser` for Microsoft Authentication Library
- [ ] Verify all authentication dependencies are installed

### ✅ Step 8: Test Authentication Flow
- [ ] Start development server: `npm run dev`
- [ ] Navigate to `http://localhost:5173`
- [ ] Click "Sign in with Whiskey House"
- [ ] Verify redirect to Microsoft login
- [ ] Sign in with a @whiskeyhouse.com account
- [ ] Verify successful authentication and redirect back to app
- [ ] Check browser developer tools for any errors

## Production Deployment Checklist

### ✅ Step 9: Production Configuration
- [ ] Update redirect URI in Azure AD to production URL
- [ ] Update VITE_AUTH_REDIRECT_URI to production URL (must use HTTPS)
- [ ] Test authentication flow in production environment
- [ ] Verify SSL certificate is valid for production domain

### ✅ Step 10: Security Validation
- [ ] Confirm only @whiskeyhouse.com users can authenticate
- [ ] Test with non-Whiskey House account (should fail)
- [ ] Verify token validation is working correctly
- [ ] Test logout functionality

## Troubleshooting

### Common Issues and Solutions

**❌ "AADSTS50011: The reply URL specified in the request does not match"**
- ✅ Check that VITE_AUTH_REDIRECT_URI exactly matches Azure AD configuration
- ✅ Ensure no trailing slashes or extra characters

**❌ "AADSTS700016: Application not found in the directory"**
- ✅ Verify VITE_WHISKEY_HOUSE_CLIENT_ID is correct
- ✅ Confirm you're using the right tenant

**❌ "AADSTS50020: User account from identity provider does not exist"**
- ✅ Ensure test user exists in Whiskey House tenant
- ✅ Verify user has @whiskeyhouse.com email address

**❌ "AADSTS65001: The user or administrator has not consented"**
- ✅ Grant admin consent in Azure AD API permissions
- ✅ Verify consent status shows "Granted"

## Next Steps After Successful Setup

- [ ] **Document User Onboarding**: Create guide for Whiskey House employees
- [ ] **Set Up Monitoring**: Configure Azure AD sign-in logs monitoring
- [ ] **Plan User Training**: Schedule training sessions for end users
- [ ] **Configure Additional Security**: Set up MFA, conditional access policies
- [ ] **Test Edge Cases**: Test with different user roles, devices, browsers

## Support Contacts

- **Azure AD Issues**: Contact Whiskey House IT Administrator
- **Application Issues**: Contact IGN Scripts Development Team
- **Microsoft Support**: Available through Azure Portal (if support plan exists)

---

**✅ Setup Complete!**
Once all items are checked, your Whiskey House SSO integration should be fully functional.
