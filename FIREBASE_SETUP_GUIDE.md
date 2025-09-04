# Firebase Setup Guide for Klymate AI

## Overview
This guide will help you properly configure Firebase for your Klymate AI application with Google authentication support.

## Prerequisites
- Firebase project created at https://console.firebase.google.com
- Google Cloud Console access for service account setup

## Step 1: Firebase Project Setup

### 1.1 Create Firebase Project
1. Go to https://console.firebase.google.com
2. Click "Create a project"
3. Enter project name (e.g., "klymate-ai")
4. Enable Google Analytics (optional)
5. Create project

### 1.2 Enable Authentication
1. In Firebase Console, go to "Authentication"
2. Click "Get started"
3. Go to "Sign-in method" tab
4. Enable the following providers:
   - **Email/Password** (for email registration)
   - **Google** (for Google sign-in)
   - **Facebook** (optional)
   - **Apple** (optional, for iOS/macOS)

### 1.3 Configure Google Sign-In
1. Click on "Google" provider
2. Enable it
3. Set your project support email
4. Add your domain to authorized domains:
   - `localhost` (for development)
   - Your production domain
5. Save

## Step 2: Frontend Configuration

### 2.1 Get Firebase Config
1. In Firebase Console, go to Project Settings (gear icon)
2. Scroll down to "Your apps"
3. Click "Add app" → Web app
4. Register your app (name: "Klymate AI Frontend")
5. Copy the config object

### 2.2 Update Frontend Environment
Replace the values in `frontend/.env.local`:

```env
# Firebase Configuration
NEXT_PUBLIC_FIREBASE_API_KEY=AIzaSyC...your_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project-id.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=123456789
NEXT_PUBLIC_FIREBASE_APP_ID=1:123456789:web:abcdef123456
```

## Step 3: Backend Configuration (Firebase Admin SDK)

### 3.1 Create Service Account
1. Go to Google Cloud Console: https://console.cloud.google.com
2. Select your Firebase project
3. Go to "IAM & Admin" → "Service Accounts"
4. Click "Create Service Account"
5. Name: "klymate-ai-backend"
6. Grant role: "Firebase Admin SDK Administrator Service Agent"
7. Create and download the JSON key file

### 3.2 Extract Service Account Details
From the downloaded JSON file, extract these values:

```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "key-id-here",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "service-account@your-project-id.iam.gserviceaccount.com",
  "client_id": "123456789",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token"
}
```

### 3.3 Update Backend Environment
Replace the values in `backend/.env`:

```env
# Firebase Admin SDK Configuration
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\nyour-private-key-content\n-----END PRIVATE KEY-----
FIREBASE_CLIENT_EMAIL=service-account@your-project-id.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-client-id
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
```

**Important:** Replace `\n` in the private key with actual newlines in the .env file.

## Step 4: Test Firebase Integration

### 4.1 Start the Applications
```bash
# Terminal 1 - Backend
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend  
cd frontend
npm run dev
```

### 4.2 Test Registration Flow
1. Go to http://localhost:3000
2. Click "Get Started"
3. Try both registration methods:
   - **Email/Password**: Fill form and submit
   - **Google Sign-In**: Click "Continue with Google"

### 4.3 Verify Firebase Console
1. Go to Firebase Console → Authentication → Users
2. You should see registered users appear here
3. Check that Google sign-in users have the correct provider

## Step 5: Authentication Flow

### How It Works Now:

#### Email/Password Registration:
1. User fills registration form
2. Frontend creates Firebase account
3. Firebase sends verification email
4. Frontend gets Firebase ID token
5. Backend verifies token and creates JWT
6. User is logged in and redirected to onboarding

#### Google Sign-In:
1. User clicks "Continue with Google"
2. Google OAuth popup appears
3. User authorizes the app
4. Firebase gets Google user info
5. Frontend gets Firebase ID token
6. Backend verifies token and creates JWT
7. User is logged in and redirected to onboarding

## Step 6: Production Considerations

### 6.1 Security Rules
Add these domains to Firebase authorized domains:
- Your production domain
- Any staging domains

### 6.2 Environment Variables
Use secure environment variable management:
- Vercel/Netlify environment variables
- AWS Secrets Manager
- Google Secret Manager

### 6.3 CORS Configuration
Update backend CORS settings for production:
```env
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

## Troubleshooting

### Common Issues:

1. **"Firebase is not initialized"**
   - Check environment variables are set correctly
   - Restart development servers after changing .env files

2. **"Invalid API key"**
   - Verify API key in Firebase Console
   - Check for extra spaces in .env file

3. **"Unauthorized domain"**
   - Add your domain to Firebase authorized domains
   - Include both with and without www

4. **Google Sign-In popup blocked**
   - Allow popups in browser
   - Check browser console for errors

5. **Backend 500 errors**
   - Check Firebase Admin SDK credentials
   - Verify service account has correct permissions

### Debug Steps:
1. Check browser console for Firebase errors
2. Check backend logs for authentication errors
3. Verify Firebase Console shows authentication attempts
4. Test with Firebase Auth Emulator for development

## Success Indicators

✅ Firebase Console shows "Authentication" is enabled  
✅ Google provider is configured and enabled  
✅ Frontend shows no Firebase initialization errors  
✅ Backend starts without Firebase credential errors  
✅ Registration with email works  
✅ Google sign-in popup appears and works  
✅ Users appear in Firebase Console → Authentication → Users  
✅ JWT tokens are generated successfully  
✅ User is redirected to onboarding after registration  

Your Firebase integration is now properly configured and ready for production use!