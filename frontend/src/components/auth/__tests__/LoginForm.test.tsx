import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import LoginForm from '../LoginForm';
import { AuthProvider } from '@/lib/auth/AuthContext';

// Mock the auth store
jest.mock('@/lib/auth/authStore', () => ({
  useAuthStore: jest.fn(() => ({
    loginWithEmail: jest.fn(),
    isLoading: false,
    error: null,
    clearError: jest.fn()
  }))
}));

describe('LoginForm', () => {
  it('renders login form', () => {
    render(
      <AuthProvider>
        <LoginForm />
      </AuthProvider>
    );

    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });

  it('handles form submission', async () => {
    const mockLoginWithEmail = jest.fn().mockResolvedValue(undefined);
    const mockOnSuccess = jest.fn();
    
    jest.spyOn(require('@/lib/auth/authStore'), 'useAuthStore').mockReturnValue({
      loginWithEmail: mockLoginWithEmail,
      isLoading: false,
      error: null,
      clearError: jest.fn()
    });

    render(
      <AuthProvider>
        <LoginForm onSuccess={mockOnSuccess} />
      </AuthProvider>
    );

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'test@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'password123' },
    });

    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() => {
      expect(mockLoginWithEmail).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123',
        rememberMe: false
      });
      expect(mockOnSuccess).toHaveBeenCalled();
    });
  });

  it('displays validation errors', async () => {
    render(
      <AuthProvider>
        <LoginForm />
      </AuthProvider>
    );

    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() => {
      expect(screen.getByText(/please enter a valid email address/i)).toBeInTheDocument();
      expect(screen.getByText(/password is required/i)).toBeInTheDocument();
    });
  });

  it('handles login error', async () => {
    const mockLoginWithEmail = jest.fn().mockRejectedValue({
      code: 'auth/wrong-password',
      message: 'Incorrect password'
    });
    
    jest.spyOn(require('@/lib/auth/authStore'), 'useAuthStore').mockReturnValue({
      loginWithEmail: mockLoginWithEmail,
      isLoading: false,
      error: null,
      clearError: jest.fn()
    });

    render(
      <AuthProvider>
        <LoginForm />
      </AuthProvider>
    );

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'invalid@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'wrongpassword' },
    });

    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() => {
      expect(mockLoginWithEmail).toHaveBeenCalledWith({
        email: 'invalid@example.com',
        password: 'wrongpassword',
        rememberMe: false
      });
      expect(screen.getByText(/incorrect password/i)).toBeInTheDocument();
    });
  });
});