/**
 * Firebase Configuration Test Utility
 * 
 * This utility helps test if Firebase is properly configured
 * Run this in browser console to check Firebase status
 */

import { auth } from '@/lib/auth/firebase'

export const testFirebaseConfig = () => {
  console.log('🔥 Firebase Configuration Test')
  console.log('================================')
  
  // Check environment variables
  const config = {
    apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
    authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
    projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
    storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
    messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
    appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
  }
  
  console.log('📋 Environment Variables:')
  Object.entries(config).forEach(([key, value]) => {
    const status = value ? '✅' : '❌'
    const displayValue = value ? (value.length > 20 ? `${value.substring(0, 20)}...` : value) : 'NOT SET'
    console.log(`${status} ${key}: ${displayValue}`)
  })
  
  // Check Firebase Auth initialization
  console.log('\n🔐 Firebase Auth Status:')
  if (auth) {
    console.log('✅ Firebase Auth initialized successfully')
    console.log(`📱 App Name: ${auth.app.name}`)
    console.log(`🆔 Project ID: ${auth.app.options.projectId}`)
    
    // Check current user
    if (auth.currentUser) {
      console.log(`👤 Current User: ${auth.currentUser.email}`)
      console.log(`✉️ Email Verified: ${auth.currentUser.emailVerified}`)
    } else {
      console.log('👤 No current user (not logged in)')
    }
  } else {
    console.log('❌ Firebase Auth not initialized')
    console.log('💡 Check your environment variables and restart the dev server')
  }
  
  // Check required variables
  const requiredVars = ['apiKey', 'authDomain', 'projectId']
  const missingVars = requiredVars.filter(key => !config[key as keyof typeof config])
  
  if (missingVars.length > 0) {
    console.log('\n⚠️ Missing Required Variables:')
    missingVars.forEach(varName => {
      console.log(`❌ NEXT_PUBLIC_FIREBASE_${varName.toUpperCase()}`)
    })
    console.log('\n📝 Add these to your .env.local file')
  } else {
    console.log('\n✅ All required Firebase variables are set')
  }
  
  // Test recommendations
  console.log('\n🛠️ Next Steps:')
  if (!auth) {
    console.log('1. Set missing environment variables in .env.local')
    console.log('2. Restart your development server (npm run dev)')
    console.log('3. Run this test again')
  } else {
    console.log('1. Try registering with email/password')
    console.log('2. Try Google sign-in')
    console.log('3. Check Firebase Console for new users')
  }
  
  return {
    isConfigured: !!auth,
    missingVars,
    config: auth ? {
      projectId: auth.app.options.projectId,
      currentUser: auth.currentUser?.email || null
    } : null
  }
}

// Auto-run in development
if (typeof window !== 'undefined' && process.env.NODE_ENV === 'development') {
  // Run test after a short delay to ensure Firebase is initialized
  setTimeout(() => {
    if (window.location.search.includes('firebase-test')) {
      testFirebaseConfig()
    }
  }, 1000)
}

export default testFirebaseConfig