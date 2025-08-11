# 🎨 Frontend Integration Guide

## 🚀 Quick Start for Frontend Team (Cheptoo & Victor)

### **Backend API is Ready!** ✅
- Authentication system working
- Database connected  
- 41+ tests passing
- API documentation available

## 📡 API Endpoints Available:

### **Base URL:** `http://localhost:8000`

### **Authentication Endpoints:**
```javascript
// Register new user
POST /api/v1/auth/register
{
  "firebase_token": "firebase_id_token_from_client"
}

// Login user  
POST /api/v1/auth/login
{
  "firebase_token": "firebase_id_token_from_client"
}

// Get user profile (requires auth)
GET /api/v1/auth/profile
Headers: { "Authorization": "Bearer jwt_access_token" }

// Refresh tokens
POST /api/v1/auth/refresh  
{
  "refresh_token": "jwt_refresh_token"
}

// Logout user
POST /api/v1/auth/logout
Headers: { "Authorization": "Bearer jwt_access_token" }
```

### **Health Check:**
```javascript
// Check if API is running
GET /health
// Returns: {"status": "healthy", "service": "Klymate-AI", "version": "1.0.0"}
```

## 🔧 Frontend Setup Options:

### **Option 1: Full Setup (Recommended)**
```bash
# Get backend running locally for development
git pull origin main
cd backend
cp .env.hackathon .env

# Edit .env - change database name:
TIDB_DATABASE=klymate_ai_cheptoo  # or klymate_ai_victor

# Setup
curl -o ca-cert.pem https://letsencrypt.org/certs/isrgrootx1.pem
pip install -r requirements.txt
python setup_database.py
python app/main.py  # Start API server
```

### **Option 2: Use Shared Backend**
- Use Tangus's running backend instance
- API available at his local server
- Focus purely on frontend development

## 🔥 Firebase Integration:

### **Frontend Firebase Setup:**
```javascript
// Firebase config (get from team)
const firebaseConfig = {
  apiKey: "your-api-key",
  authDomain: "klymate-ai-hackathon.firebaseapp.com",
  projectId: "klymate-ai-hackathon",
  // ... other config
};

// Initialize Firebase
import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
```

### **Authentication Flow:**
```javascript
// 1. User signs in with Firebase
import { signInWithEmailAndPassword } from 'firebase/auth';

const signIn = async (email, password) => {
  try {
    const userCredential = await signInWithEmailAndPassword(auth, email, password);
    const firebaseToken = await userCredential.user.getIdToken();
    
    // 2. Send Firebase token to your backend
    const response = await fetch('http://localhost:8000/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ firebase_token: firebaseToken })
    });
    
    const data = await response.json();
    
    // 3. Store JWT tokens for API calls
    localStorage.setItem('access_token', data.tokens.access_token);
    localStorage.setItem('refresh_token', data.tokens.refresh_token);
    
    return data.user;
  } catch (error) {
    console.error('Login failed:', error);
  }
};
```

### **Making Authenticated API Calls:**
```javascript
// Helper function for authenticated requests
const apiCall = async (endpoint, options = {}) => {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch(`http://localhost:8000${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      ...options.headers
    }
  });
  
  if (response.status === 401) {
    // Token expired, refresh it
    await refreshToken();
    // Retry the request
    return apiCall(endpoint, options);
  }
  
  return response.json();
};

// Example: Get user profile
const getUserProfile = () => apiCall('/api/v1/auth/profile');
```

## 📊 API Documentation:

### **Interactive Docs:** `http://localhost:8000/docs`
- Complete API documentation
- Try endpoints directly in browser
- See request/response examples

### **OpenAPI Spec:** `http://localhost:8000/openapi.json`
- Machine-readable API specification
- Can generate client code automatically

## 🎯 Development Workflow:

### **Day 1: Authentication**
1. Set up Firebase in frontend
2. Implement login/register UI
3. Connect to backend auth endpoints
4. Test authentication flow

### **Day 2: Core Features**
1. Build main dashboard UI
2. Create habit tracking interface  
3. Add user profile management
4. Connect to backend APIs (as they're built)

### **Day 3: Polish & Integration**
1. Improve UI/UX
2. Add error handling
3. Optimize performance
4. Final integration testing

## 🆘 Troubleshooting:

### **CORS Issues:**
```javascript
// If you get CORS errors, backend is configured to allow:
// - http://localhost:3000 (React default)
// - http://localhost:5173 (Vite default)
```

### **API Not Responding:**
```bash
# Check if backend is running
curl http://localhost:8000/health

# Start backend if needed
cd backend && python app/main.py
```

### **Authentication Errors:**
1. Check Firebase configuration
2. Verify Firebase token is valid
3. Check network requests in browser dev tools

## 📞 Quick Commands:

```bash
# Test API health
curl http://localhost:8000/health

# Test authentication (with real Firebase token)
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"firebase_token": "your_firebase_token"}'

# View API docs
open http://localhost:8000/docs
```

---

**🎨 Frontend Success Tips:**
- **Start with authentication** - it's the foundation
- **Use API docs** - they're interactive and up-to-date  
- **Mock data first** - don't wait for all backend APIs
- **Ask for help** - backend team is here to support you!**