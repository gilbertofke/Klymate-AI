import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { OnboardingWizard } from '../OnboardingWizard'
import { useEnhancedOnboarding } from '@/lib/hooks/useEnhancedOnboarding'
import { categorizeError } from '@/lib/utils/errorHandling'

// Mock the enhanced onboarding hook
jest.mock('@/lib/hooks/useEnhancedOnboarding')
jest.mock('@/lib/auth/authStore')
jest.mock('@/lib/stores/onboardingStore')

const mockUseEnhancedOnboarding = useEnhancedOnboarding as jest.MockedFunction<typeof useEnhancedOnboarding>

// Mock store data
const mockStoreData = {
  currentStep: 5, // Completion step
  totalSteps: 5,
  progress: 100,
  collectedData: {
    location: 'Test City',
    household_size: 2,
    primary_transport: 'car',
    diet_type: 'omnivore',
  },
  stepValidation: { 1: true, 2: true, 3: true, 4: true, 5: true },
  nextStep: jest.fn(),
  previousStep: jest.fn(),
  updateData: jest.fn(),
  validateStep: jest.fn(),
  canProceed: jest.fn(() => true),
  resetOnboarding: jest.fn(),
}

jest.mock('@/lib/stores/onboardingStore', () => ({
  useOnboardingStore: () => mockStoreData,
}))

jest.mock('@/lib/auth/authStore', () => ({
  useAuthStore: {
    getState: () => ({
      user: { id: '1', email: 'test@example.com' },
      setUser: jest.fn(),
      debouncedRefreshUser: jest.fn(),
    }),
  },
}))

const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
})

const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const queryClient = createTestQueryClient()
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )
}

describe('OnboardingWizard Error Handling', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('displays network error with retry option', async () => {
    const mockError = {
      type: 'network' as const,
      message: 'Network connection failed',
      userMessage: 'Unable to connect to the server. Please check your internet connection and try again.',
      retryable: true,
    }

    const mockSubmit = jest.fn().mockRejectedValue(new Error('Network Error'))
    const mockRetry = jest.fn()

    mockUseEnhancedOnboarding.mockReturnValue({
      isLoading: false,
      isRetrying: false,
      error: mockError,
      retryCount: 1,
      progress: 0,
      currentStage: undefined,
      currentMessage: undefined,
      stages: [],
      submitOnboarding: mockSubmit,
      retry: mockRetry,
      cancel: jest.fn(),
      clearError: jest.fn(),
      canRetry: true,
      userErrorMessage: mockError.userMessage,
      mutate: mockSubmit,
      mutateAsync: mockSubmit,
      isPending: false,
      isError: true,
      reset: jest.fn(),
    })

    render(
      <TestWrapper>
        <OnboardingWizard />
      </TestWrapper>
    )

    // Check that error is displayed
    expect(screen.getByText(/Unable to connect to the server/)).toBeInTheDocument()
    
    // Check that retry button is present
    const retryButton = screen.getByText(/Try Again/i)
    expect(retryButton).toBeInTheDocument()
    
    // Test retry functionality
    fireEvent.click(retryButton)
    expect(mockRetry).toHaveBeenCalled()
  })

  it('displays validation error without retry option', async () => {
    const mockError = {
      type: 'validation' as const,
      message: 'Validation failed',
      userMessage: 'Please check your input and correct any errors.',
      retryable: false,
      details: {
        location: ['This field is required'],
        household_size: ['Must be a positive number'],
      },
    }

    mockUseEnhancedOnboarding.mockReturnValue({
      isLoading: false,
      isRetrying: false,
      error: mockError,
      retryCount: 0,
      progress: 0,
      currentStage: undefined,
      currentMessage: undefined,
      stages: [],
      submitOnboarding: jest.fn(),
      retry: jest.fn(),
      cancel: jest.fn(),
      clearError: jest.fn(),
      canRetry: false,
      userErrorMessage: mockError.userMessage,
      mutate: jest.fn(),
      mutateAsync: jest.fn(),
      isPending: false,
      isError: true,
      reset: jest.fn(),
    })

    render(
      <TestWrapper>
        <OnboardingWizard />
      </TestWrapper>
    )

    // Check that error is displayed
    expect(screen.getByText(/Please check your input and correct any errors/)).toBeInTheDocument()
    
    // Check that retry button is NOT present for validation errors
    expect(screen.queryByText(/Try Again/i)).not.toBeInTheDocument()
    
    // Check that dismiss button is present
    expect(screen.getByText(/Dismiss/i)).toBeInTheDocument()
  })

  it('shows loading states during onboarding submission', async () => {
    mockUseEnhancedOnboarding.mockReturnValue({
      isLoading: true,
      isRetrying: false,
      error: null,
      retryCount: 0,
      progress: 50,
      currentStage: 'Calculating',
      currentMessage: 'Calculating your carbon footprint...',
      stages: [
        { key: 'validating', label: 'Validating', completed: true, current: false, error: false },
        { key: 'submitting', label: 'Submitting', completed: true, current: false, error: false },
        { key: 'calculating', label: 'Calculating', completed: false, current: true, error: false },
        { key: 'personalizing', label: 'Personalizing', completed: false, current: false, error: false },
        { key: 'finalizing', label: 'Finalizing', completed: false, current: false, error: false },
      ],
      submitOnboarding: jest.fn(),
      retry: jest.fn(),
      cancel: jest.fn(),
      clearError: jest.fn(),
      canRetry: false,
      userErrorMessage: null,
      mutate: jest.fn(),
      mutateAsync: jest.fn(),
      isPending: true,
      isError: false,
      reset: jest.fn(),
    })

    render(
      <TestWrapper>
        <OnboardingWizard />
      </TestWrapper>
    )

    // Check that loading overlay is present
    expect(screen.getByText(/Calculating your carbon footprint/)).toBeInTheDocument()
    
    // Check that stage indicator shows current progress
    expect(screen.getByText('Calculating')).toBeInTheDocument()
    
    // Check that save button is disabled during loading
    const saveButton = screen.getByTitle('Save progress')
    expect(saveButton).toBeDisabled()
  })

  it('shows retry information during retry attempts', async () => {
    mockUseEnhancedOnboarding.mockReturnValue({
      isLoading: false,
      isRetrying: true,
      error: {
        type: 'server' as const,
        message: 'Server error',
        userMessage: 'The server is experiencing issues. Please try again in a few moments.',
        retryable: true,
      },
      retryCount: 2,
      progress: 0,
      currentStage: undefined,
      currentMessage: undefined,
      stages: [],
      submitOnboarding: jest.fn(),
      retry: jest.fn(),
      cancel: jest.fn(),
      clearError: jest.fn(),
      canRetry: true,
      userErrorMessage: 'The server is experiencing issues. Please try again in a few moments.',
      mutate: jest.fn(),
      mutateAsync: jest.fn(),
      isPending: false,
      isError: true,
      reset: jest.fn(),
    })

    render(
      <TestWrapper>
        <OnboardingWizard />
      </TestWrapper>
    )

    // Check that retry information is displayed
    expect(screen.getByText(/Retrying... \(Attempt 2 of 3\)/)).toBeInTheDocument()
    
    // Check that server error message is shown
    expect(screen.getByText(/The server is experiencing issues/)).toBeInTheDocument()
  })

  it('shows offline indicator when network is unavailable', async () => {
    // Mock navigator.onLine
    Object.defineProperty(navigator, 'onLine', {
      writable: true,
      value: false,
    })

    mockUseEnhancedOnboarding.mockReturnValue({
      isLoading: false,
      isRetrying: false,
      error: null,
      retryCount: 0,
      progress: 0,
      currentStage: undefined,
      currentMessage: undefined,
      stages: [],
      submitOnboarding: jest.fn(),
      retry: jest.fn(),
      cancel: jest.fn(),
      clearError: jest.fn(),
      canRetry: false,
      userErrorMessage: null,
      mutate: jest.fn(),
      mutateAsync: jest.fn(),
      isPending: false,
      isError: false,
      reset: jest.fn(),
    })

    render(
      <TestWrapper>
        <OnboardingWizard />
      </TestWrapper>
    )

    // Check that offline indicator is shown
    expect(screen.getByText(/You appear to be offline/)).toBeInTheDocument()

    // Restore navigator.onLine
    Object.defineProperty(navigator, 'onLine', {
      writable: true,
      value: true,
    })
  })
})

describe('Error Categorization', () => {
  it('correctly categorizes network errors', () => {
    const networkError = { code: 'ERR_NETWORK' }
    const result = categorizeError(networkError)
    
    expect(result.type).toBe('network')
    expect(result.retryable).toBe(true)
    expect(result.userMessage).toContain('internet connection')
  })

  it('correctly categorizes CORS errors', () => {
    const corsError = { 
      response: { status: 0 },
      message: 'Network Error'
    }
    const result = categorizeError(corsError)
    
    expect(result.type).toBe('cors')
    expect(result.retryable).toBe(true)
  })

  it('correctly categorizes validation errors', () => {
    const validationError = {
      response: {
        status: 422,
        data: {
          detail: 'Validation failed',
          errors: {
            location: ['This field is required']
          }
        }
      }
    }
    const result = categorizeError(validationError)
    
    expect(result.type).toBe('validation')
    expect(result.retryable).toBe(false)
    expect(result.statusCode).toBe(422)
  })

  it('correctly categorizes server errors', () => {
    const serverError = {
      response: {
        status: 500,
        data: {
          detail: 'Internal server error'
        }
      }
    }
    const result = categorizeError(serverError)
    
    expect(result.type).toBe('server')
    expect(result.retryable).toBe(true)
    expect(result.statusCode).toBe(500)
  })
})