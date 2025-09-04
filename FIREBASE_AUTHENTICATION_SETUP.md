# Firebase Authentication Setup Guide

## 🚨 Current Issue
You're getting 500 errors because Firebase isn't properly configured. Here's how to fix it:

## ✅ Step 1: Enable Firebase Authentication

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Select your project: **klymate-ai-dbf02**
3. Click **Authentication** in the left sidebar
4. Click **Get started** if you haven't enabled it yet
5. Go to **Sign-in method** tab
6. Enable these providers:
   - ✅ **Email/Password** (click Enable)
   - ✅ **Google** (click Enable, add your support email)

## ✅ Step 2: Add Authorized Domains

1. In Authentication → Settings → Authorized domains
2. Add these domains:
   - `localhost` (for development)
   - `127.0.0.1` (for development)
   - Your production domain (when ready)

## ✅ Step 3: Create Service Account (Backend)

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Select project: **klymate-ai-dbf02**
3. Go to **IAM & Admin** → **Service Accounts**
4. Click **Create Service Account**
5. Name: `klymate-ai-backend`
6. Description: `Backend service for Klymate AI`
7. Click **Create and Continue**
8. Add role: **Firebase Admin SDK Administrator Service Agent**
9. Click **Continue** → **Done**

## ✅ Step 4: Download Service Account Key

1. In Service Accounts, find your new service account
2. Click the **Actions** menu (3 dots)
3. Click **Manage keys**
4. Click **Add Key** → **Create new key**
5. Choose **JSON** format
6. Click **Create** - this downloads the JSON file

## ✅ Step 5: Update Backend Configuration

Open the downloaded JSON file and copy these values to `backend/.env`:

```env
FIREBASE_PROJECT_ID=klymate-ai-dbf02
FIREBASE_PRIVATE_KEY_ID=[copy from "private_key_id" in JSON]
FIREBASE_PRIVATE_KEY="[copy from "private_key" in JSON - keep the quotes and newlines]"
FIREBASE_CLIENT_EMAIL=[copy from "client_email" in JSON]
FIREBASE_CLIENT_ID=[copy from "client_id" in JSON]
```

**Important**: The private key should look like:
```
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG...\n-----END PRIVATE KEY-----\n"
```

## ✅ Step 6: Test the Setup

1. **Start Backend**:
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload
   ```

2. **Start Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

3. **Check Status**:
   - Visit http://localhost:3000
   - Look for "Firebase: Connected" in bottom right corner
   - Try registering a new account

## 🔧 Quick Test Commands

Test Firebase connection:
```bash
# Backend test
cd backend
python -c "from app.utils.firebase_config import FirebaseConfig; FirebaseConfig.initialize(); print('✅ Firebase Backend OK')"

# Frontend test - open browser console at localhost:3000
# Should see: "Firebase initialized successfully"
```

## 🐛 Troubleshooting

**Still getting 500 errors?**

1. **Check Backend Logs**:
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload --log-level debug
   ```

2. **Check Frontend Console**:
   - Open browser dev tools (F12)
   - Look for Firebase errors in console

3. **Common Issues**:
   - Private key format: Must include `\n` for newlines
   - Service account permissions: Needs Firebase Admin role
   - CORS: Backend should allow `http://localhost:3000`

**Need help?** The app has fallback authentication, so users can still register without Firebase while you fix this.

## 🎯 Expected Result

After setup:
- ✅ No more 500 errors
- ✅ Firebase status shows "Connected"
- ✅ Users can register with email/password
- ✅ Google Sign-In works
- ✅ Smooth flow from landing page → registration → onboarding → dashboard

Your authentication flow will be production-ready! 🚀