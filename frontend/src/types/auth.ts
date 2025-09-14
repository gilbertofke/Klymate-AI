import { User as FirebaseUser } from 'firebase/auth'

export interface User extends FirebaseUser {
  onboarding_completed?: boolean;
}

export interface LoginCredentials {
  email: string;
  password: string;
  rememberMe?: boolean;
}
