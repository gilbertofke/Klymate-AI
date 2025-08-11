# 🎨 Frontend Architecture Guide for Klymate AI

## 📊 **Backend Analysis Summary**

Your backend now includes comprehensive authentication with password recovery and security features:

### **Backend Security Features:**
- ✅ **Firebase Authentication** with JWT token management
- ✅ **Password Recovery** via Firebase and email
- ✅ **Password Hashing** with bcrypt for local auth backup
- ✅ **Token Refresh** mechanism
- ✅ **Secure Password Validation** with strength requirements
- ✅ **RESTful API** with FastAPI + comprehensive OpenAPI docs

---

## 🚀 **Recommended Frontend Stack: React + TypeScript**

Since your team is familiar with React, here's a flexible architecture that works with any React setup.

### **Tech Stack Options:**

```typescript
// Option 1: Create React App (Simple & Familiar)
{
  "framework": "Create React App",
  "language": "TypeScript",
  "routing": "React Router v6",
  "styling": "Tailwind CSS + Headless UI",
  "stateManagement": "Zustand + TanStack Query",
  "authentication": "Firebase SDK + Custom JWT handling"
}

// Option 2: Vite (Faster Development)
{
  "framework": "Vite + React",
  "language": "TypeScript", 
  "routing": "React Router v6",
  "styling": "Tailwind CSS + Radix UI",
  "stateManagement": "Zustand + TanStack Query",
  "authentication": "Firebase SDK + Custom JWT handling"
}

// Option 3: Next.js (Full-Stack)
{
  "framework": "Next.js 14",
  "language": "TypeScript",
  "routing": "App Router",
  "styling": "Tailwind CSS + shadcn/ui", 
  "stateManagement": "Zustand + TanStack Query",
  "authentication": "Firebase SDK + Custom JWT handling"
}
```

---

## 🔐 **Authentication Architecture with Password Recovery**

### **Complete Auth Flow Implementation**

```typescript
// lib/auth/auth-service.ts
import { 
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  sendPasswordResetEmail,
  confirmPasswordReset,
  signOut
} from 'firebase/auth';
import { auth } from './firebase-config';

class AuthService {
  // Sign up with email/password
  async signUp(email: string, password: string) {
    try {
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      const firebaseToken = await userCredential.user.getIdToken();
      
      // Exchange for JWT tokens with your backend
      const response = await fetch('/api/v1/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ firebase_token: firebaseToken })
      });
      
      const { tokens, user } = await response.json();
      this.setTokens(tokens);
      return { user, tokens };
    } catch (error) {
      throw new Error(`Sign up failed: ${error.message}`);
    }
  }

  // Sign in with email/password
  async signIn(email: string, password: string) {
    try {
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      const firebaseToken = await userCredential.user.getIdToken();
      
      // Exchange for JWT tokens
      const response = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ firebase_token: firebaseToken })
      });
      
      const { tokens, user } = await response.json();
      this.setTokens(tokens);
      return { user, tokens };
    } catch (error) {
      throw new Error(`Sign in failed: ${error.message}`);
    }
  }

  // Password recovery
  async requestPasswordReset(email: string) {
    try {
      // Firebase client-side password reset
      await sendPasswordResetEmail(auth, email);
      
      // Also notify your backend for logging/analytics
      await fetch('/api/v1/auth/password-reset', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      });
      
      return { success: true, message: 'Password reset email sent' };
    } catch (error) {
      throw new Error(`Password reset failed: ${error.message}`);
    }
  }

  // Confirm password reset
  async confirmPasswordReset(oobCode: string, newPassword: string) {
    try {
      await confirmPasswordReset(auth, oobCode, newPassword);
      return { success: true, message: 'Password reset successful' };
    } catch (error) {
      throw new Error(`Password reset confirmation failed: ${error.message}`);
    }
  }

  // Token management
  private setTokens(tokens: any) {
    localStorage.setItem('access_token', tokens.access_token);
    localStorage.setItem('refresh_token', tokens.refresh_token);
  }

  async refreshTokens() {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) throw new Error('No refresh token');

    const response = await fetch('/api/v1/auth/refresh', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken })
    });

    const { tokens } = await response.json();
    this.setTokens(tokens);
    return tokens;
  }

  async signOut() {
    try {
      await signOut(auth);
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    } catch (error) {
      console.error('Sign out error:', error);
    }
  }
}

export const authService = new AuthService();
```

### **React Context for Authentication**

```typescript
// contexts/AuthContext.tsx
import React, { createContext, useContext, useEffect, useState } from 'react';
import { User } from 'firebase/auth';
import { auth } from '../lib/auth/firebase-config';
import { authService } from '../lib/auth/auth-service';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<any>;
  signUp: (email: string, password: string) => Promise<any>;
  signOut: () => Promise<void>;
  requestPasswordReset: (email: string) => Promise<any>;
  confirmPasswordReset: (code: string, password: string) => Promise<any>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = auth.onAuthStateChanged((user) => {
      setUser(user);
      setLoading(false);
    });

    return unsubscribe;
  }, []);

  const value = {
    user,
    loading,
    signIn: authService.signIn.bind(authService),
    signUp: authService.signUp.bind(authService),
    signOut: authService.signOut.bind(authService),
    requestPasswordReset: authService.requestPasswordReset.bind(authService),
    confirmPasswordReset: authService.confirmPasswordReset.bind(authService),
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
```

---

## 🔒 **Password Recovery Components**

### **Password Reset Request Form**

```typescript
// components/auth/PasswordResetForm.tsx
import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';

export function PasswordResetForm() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  
  const { requestPasswordReset } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setMessage('');

    try {
      await requestPasswordReset(email);
      setMessage('Password reset email sent! Check your inbox.');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-6 text-center">Reset Password</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700">
            Email Address
          </label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500"
            placeholder="Enter your email"
          />
        </div>

        {error && (
          <div className="text-red-600 text-sm bg-red-50 p-3 rounded-md">
            {error}
          </div>
        )}

        {message && (
          <div className="text-green-600 text-sm bg-green-50 p-3 rounded-md">
            {message}
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
        >
          {loading ? 'Sending...' : 'Send Reset Email'}
        </button>
      </form>
    </div>
  );
}
```

### **Password Reset Confirmation Form**

```typescript
// components/auth/PasswordResetConfirmForm.tsx
import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useSearchParams, useNavigate } from 'react-router-dom';

export function PasswordResetConfirmForm() {
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [passwordStrength, setPasswordStrength] = useState<{
    isStrong: boolean;
    issues: string[];
  }>({ isStrong: false, issues: [] });
  
  const { confirmPasswordReset } = useAuth();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  
  const oobCode = searchParams.get('oobCode');

  useEffect(() => {
    if (!oobCode) {
      setError('Invalid reset link');
    }
  }, [oobCode]);

  // Password strength validation
  useEffect(() => {
    if (password) {
      const issues = [];
      
      if (password.length < 8) {
        issues.push('At least 8 characters long');
      }
      if (!/[A-Z]/.test(password)) {
        issues.push('One uppercase letter');
      }
      if (!/[a-z]/.test(password)) {
        issues.push('One lowercase letter');
      }
      if (!/\d/.test(password)) {
        issues.push('One number');
      }
      if (!/[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/.test(password)) {
        issues.push('One special character');
      }
      
      setPasswordStrength({
        isStrong: issues.length === 0,
        issues
      });
    }
  }, [password]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!passwordStrength.isStrong) {
      setError('Password does not meet security requirements');
      return;
    }
    
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await confirmPasswordReset(oobCode!, password);
      navigate('/login', { 
        state: { message: 'Password reset successful! Please sign in.' }
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (!oobCode) {
    return (
      <div className="max-w-md mx-auto bg-white p-6 rounded-lg shadow-md">
        <div className="text-red-600 text-center">
          Invalid or expired reset link
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-md mx-auto bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-6 text-center">Set New Password</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="password" className="block text-sm font-medium text-gray-700">
            New Password
          </label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500"
          />
          
          {password && !passwordStrength.isStrong && (
            <div className="mt-2 text-sm text-red-600">
              <p>Password must include:</p>
              <ul className="list-disc list-inside">
                {passwordStrength.issues.map((issue, index) => (
                  <li key={index}>{issue}</li>
                ))}
              </ul>
            </div>
          )}
          
          {password && passwordStrength.isStrong && (
            <div className="mt-2 text-sm text-green-600">
              Password meets security requirements ✓
            </div>
          )}
        </div>

        <div>
          <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700">
            Confirm New Password
          </label>
          <input
            type="password"
            id="confirmPassword"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500"
          />
        </div>

        {error && (
          <div className="text-red-600 text-sm bg-red-50 p-3 rounded-md">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={loading || !passwordStrength.isStrong}
          className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
        >
          {loading ? 'Updating...' : 'Update Password'}
        </button>
      </form>
    </div>
  );
}
```

---

## 🛡️ **Security Best Practices**

### **1. Token Management**

```typescript
// lib/api/api-client.ts
import { authService } from '../auth/auth-service';

class APIClient {
  private baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    let accessToken = localStorage.getItem('access_token');

    const makeRequest = async (token: string | null) => {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...(token && { Authorization: `Bearer ${token}` }),
          ...options.headers,
        },
      });

      if (response.status === 401 && token) {
        // Token expired, try to refresh
        try {
          const newTokens = await authService.refreshTokens();
          accessToken = newTokens.access_token;
          
          // Retry request with new token
          return fetch(`${this.baseURL}${endpoint}`, {
            ...options,
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${accessToken}`,
              ...options.headers,
            },
          });
        } catch (refreshError) {
          // Refresh failed, redirect to login
          authService.signOut();
          window.location.href = '/login';
          throw new Error('Session expired');
        }
      }

      return response;
    };

    const response = await makeRequest(accessToken);

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
  }
}

export const apiClient = new APIClient();
```

### **2. Protected Routes**

```typescript
// components/auth/ProtectedRoute.tsx
import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-green-500"></div>
      </div>
    );
  }

  if (!user) {
    // Redirect to login with return url
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
}
```

### **3. Input Validation & Sanitization**

```typescript
// utils/validation.ts
export const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const sanitizeInput = (input: string): string => {
  return input.trim().replace(/[<>]/g, '');
};

export const validatePassword = (password: string): {
  isValid: boolean;
  errors: string[];
} => {
  const errors: string[] = [];
  
  if (password.length < 8) {
    errors.push('Password must be at least 8 characters long');
  }
  
  if (!/[A-Z]/.test(password)) {
    errors.push('Password must contain at least one uppercase letter');
  }
  
  if (!/[a-z]/.test(password)) {
    errors.push('Password must contain at least one lowercase letter');
  }
  
  if (!/\d/.test(password)) {
    errors.push('Password must contain at least one number');
  }
  
  if (!/[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/.test(password)) {
    errors.push('Password must contain at least one special character');
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
};
```

---

## 📱 **Complete App Structure**

```
src/
├── components/
│   ├── auth/
│   │   ├── LoginForm.tsx
│   │   ├── SignUpForm.tsx
│   │   ├── PasswordResetForm.tsx
│   │   ├── PasswordResetConfirmForm.tsx
│   │   └── ProtectedRoute.tsx
│   ├── ui/
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   └── LoadingSpinner.tsx
│   └── dashboard/
│       ├── HabitTracker.tsx
│       ├── AICoach.tsx
│       └── Analytics.tsx
├── contexts/
│   └── AuthContext.tsx
├── lib/
│   ├── auth/
│   │   ├── firebase-config.ts
│   │   └── auth-service.ts
│   └── api/
│       └── api-client.ts
├── pages/
│   ├── Login.tsx
│   ├── SignUp.tsx
│   ├── PasswordReset.tsx
│   ├── Dashboard.tsx
│   └── Profile.tsx
├── utils/
│   ├── validation.ts
│   └── constants.ts
└── App.tsx
```

---

## 🚀 **Getting Started**

### **1. Setup Firebase**

```bash
npm install firebase
```

```typescript
// lib/auth/firebase-config.ts
import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';

const firebaseConfig = {
  // Your Firebase config
};

export const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
```

### **2. Setup Routing**

```bash
npm install react-router-dom
```

```typescript
// App.tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/auth/ProtectedRoute';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<SignUp />} />
          <Route path="/password-reset" element={<PasswordReset />} />
          <Route path="/reset-password" element={<PasswordResetConfirm />} />
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
```

This architecture provides a solid foundation for your React frontend with comprehensive authentication, password recovery, and security best practices. The team can choose their preferred React setup (CRA, Vite, or Next.js) and adapt these patterns accordingly.