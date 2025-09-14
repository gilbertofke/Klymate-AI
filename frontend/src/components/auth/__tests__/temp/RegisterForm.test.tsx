/**
 * @jest-environment jsdom
 */

import { describe, it, expect, jest, beforeEach } from '@jest/globals';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import RegisterForm from '../../RegisterForm';

// Mock the AuthContext
jest.mock('@/lib/auth/AuthContext', () => ({
  AuthProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

// Mock the auth store
const mockRegisterWithEmail = jest.fn();
const mockClearError = jest.fn();

jest.mock('@/lib/auth/authStore', () => ({
  useAuthStore: () => ({
    registerWithEmail: mockRegisterWithEmail,
    isLoading: false,
    error: null,
    clearError: mockClearError,
  }),
}));

// Mock the next/navigation module
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}));

describe('RegisterForm', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders register form', async () => {
    render(<RegisterForm />);

    await waitFor(() => {
      expect(screen.getByLabelText(/full name/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/email address/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/^password$/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /create account/i })).toBeInTheDocument();
    });
  });

  it('handles successful form submission', async () => {
    mockRegisterWithEmail.mockResolvedValueOnce(undefined);
    
    render(<RegisterForm />);

    // Fill out the form
    fireEvent.change(screen.getByLabelText(/full name/i), {
      target: { value: 'Test User' },
    });
    fireEvent.change(screen.getByLabelText(/email address/i), {
      target: { value: 'test@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/^password$/i), {
      target: { value: 'Password123!' },
    });
    fireEvent.change(screen.getByLabelText(/confirm password/i), {
      target: { value: 'Password123!' },
    });

    // Check the terms checkbox and wait for validation to complete
    const termsCheckbox = screen.getByLabelText(/I agree to the Terms/i);
    await waitFor(() => {
      fireEvent.click(termsCheckbox);
      const submitButton = screen.getByRole('button', { name: /create account/i });
      expect(submitButton).not.toBeDisabled();
      fireEvent.click(submitButton);
    });

    // Verify that registerWithEmail was called with the correct data
    await waitFor(
      () => {
        expect(mockRegisterWithEmail).toHaveBeenCalledWith({
          email: 'test@example.com',
          password: 'Password123!',
          name: 'Test User',
          acceptTerms: true,
        });
      },
      { timeout: 3000 }
    );
  });

  it('displays validation errors', async () => {
    render(<RegisterForm />);

    // Submit form without filling it out
    fireEvent.click(screen.getByLabelText(/I agree to the Terms/i));
    fireEvent.click(screen.getByRole('button', { name: /create account/i }));

    // Wait for error messages and verify them
    await waitFor(() => {
      expect(screen.getByText(/name must be at least 2 characters/i)).toBeInTheDocument();
      expect(screen.getByText(/please enter a valid email address/i)).toBeInTheDocument();
      expect(screen.getByText(/password must be at least 8 characters/i)).toBeInTheDocument();
    });
  });

  it('validates password requirements', async () => {
    render(<RegisterForm />);

    // Test weak password
    fireEvent.change(screen.getByLabelText(/^password$/i), {
      target: { value: 'weak' },
    });

    // Wait for password validation error messages
    await waitFor(() => {
      expect(screen.getByText(/password must be at least 8 characters/i)).toBeInTheDocument();
      expect(screen.getByText(/password must contain at least one uppercase letter/i)).toBeInTheDocument();
      expect(screen.getByText(/password must contain at least one number/i)).toBeInTheDocument();
      expect(screen.getByText(/password must contain at least one special character/i)).toBeInTheDocument();
    });
  });

  it('validates email format', async () => {
    render(<RegisterForm />);

    // Fill out the form with invalid email
    fireEvent.change(screen.getByLabelText(/full name/i), {
      target: { value: 'Test User' },
    });
    
    // Wait for input validation to trigger
    await waitFor(() => {
      fireEvent.change(screen.getByLabelText(/email address/i), {
        target: { value: 'invalid-email' },
      });
      fireEvent.change(screen.getByLabelText(/^password$/i), {
        target: { value: 'Password123!' },
      });
      fireEvent.change(screen.getByLabelText(/confirm password/i), {
        target: { value: 'Password123!' },
      });

      // Check the terms checkbox
      fireEvent.click(screen.getByLabelText(/I agree to the Terms/i));
    });

    // Submit form and wait for validation errors
    const submitButton = screen.getByRole('button', { name: /create account/i });
    fireEvent.click(submitButton);

    // Wait for the error message to appear
    await waitFor(
      () => {
        const emailError = screen.queryByText(/please enter a valid email address/i);
        expect(emailError).toBeInTheDocument();
      },
      { timeout: 3000 }
    );
  });

  it('validates password confirmation match', async () => {
    render(<RegisterForm />);

    // Enter different passwords
    fireEvent.change(screen.getByLabelText(/^password$/i), {
      target: { value: 'Password123!' },
    });
    fireEvent.change(screen.getByLabelText(/confirm password/i), {
      target: { value: 'DifferentPassword123!' },
    });

    fireEvent.click(screen.getByRole('button', { name: /create account/i }));

    // Wait for the error message to appear
    await waitFor(() => {
      expect(screen.getByText(/passwords don't match/i)).toBeInTheDocument();
    });
  });
});
