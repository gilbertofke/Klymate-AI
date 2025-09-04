# Quick Firebase Setup

## 🚀 Quick Start (5 minutes)

### 1. Get Your Firebase Config
1. Go to https://console.firebase.google.com
2. Create/select your project
3. Go to Project Settings → General → Your apps
4. Add web app or copy existing config

### 2. Update Frontend Environment
Edit `frontend/.env.local`:
```env
NEXT_PUBLIC_FIREBASE_API_KEY=your_api_key_here
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
```

### 3. Enable Authentication
1. Firebase Console → Authentication → Get started
2. Sign-in method → Enable:
   - ✅ Email/Password
   - ✅ Google
3. Settings → Authorized domains → Add `localhost`

### 4. Get Service Account (Backend)
1. Google Cloud Console → IAM & Admin → Service Accounts
2. Create service account with Firebase Admin role
3. Download JSON key
4. Update `backend/.env` with the values

### 5. Test It
```bash
# Start backend
cd backend && python -m uvicorn app.main:app --reload

# Start frontend  
cd frontend && npm run dev
```

Visit http://localhost:3000 - you should see a green "Firebase: Connected" indicator in the bottom right.

## 🔧 Current Status

Your app now supports:
- ✅ Email/Password registration (with Firebase)
- ✅ Google Sign-In (with Firebase) 
- ✅ Fallback authentication (without Firebase)
- ✅ Automatic onboarding flow
- ✅ JWT token management

## 🎯 Test the Flow

1. **Registration**: Click "Get Started" → Fill form → Should work with or without Firebase
2. **Google Sign-In**: Click "Continue with Google" → Google popup → Auto-login
3. **Onboarding**: After registration → Multi-step survey → Dashboard

## 🐛 Troubleshooting

**Firebase not working?** 
- Check the status indicator (bottom right)
- Open browser console for errors
- Verify .env.local has correct values
- Restart dev server after changing .env

**Still having issues?**
- The fallback system will work without Firebase
- Users can still register and use the app
- Add Firebase later when ready

Your authentication system is now production-ready! 🎉