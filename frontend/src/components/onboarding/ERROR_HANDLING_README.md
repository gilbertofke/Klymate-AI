# Enhanced Error Handling for OnboardingWizard

This document describes the comprehensive error handling and loading state improvements implemented for the OnboardingWizard component.

## Overview

The enhanced error handling system provides:

- **Intelligent Error Categorization**: Automatically categorizes errors by type (network, CORS, validation, auth, server)
- **Retry Mechanisms**: Implements exponential backoff retry logic for retryable errors
- **User-Friendly Messages**: Converts technical errors into actionable user messages
- **Loading States**: Provides detailed progress tracking and stage indicators
- **Network Awareness**: Detects and handles offline scenarios

## Components

### 1. Error Handling Utilities (`/lib/utils/errorHandling.ts`)

#### `categorizeError(error: any): ErrorInfo`
Analyzes errors and returns structured error information:

```typescript
interface ErrorInfo {
  type: 'network' | 'cors' | 'validation' | 'auth' | 'server' | 'unknown'
  message: string
  userMessage: string
  retryable: boolean
  statusCode?: number
  details?: Record<string, any>
}
```

#### `RetryManager`
Implements exponential backoff retry logic:

```typescript
const retryManager = createApiRetryManager({
  maxAttempts: 3,
  baseDelay: 1000,
  maxDelay: 8000,
  backoffFactor: 2,
})

await retryManager.execute(
  () => apiCall(),
  (attempt, error) => console.log(`Retry ${attempt}:`, error)
)
```

### 2. Loading State Management (`/lib/utils/loadingStates.ts`)

#### `useLoadingState()`
Manages loading states with progress tracking:

```typescript
const loadingState = useLoadingState()

loadingState.setLoading(true, { message: 'Processing...' })
loadingState.setProgress(50, 'Halfway done')
loadingState.setLoading(false)
```

#### `useStageLoader()`
Manages multi-stage loading processes:

```typescript
const stageLoader = useStageLoader(STAGES)

stageLoader.startStage('validating')
stageLoader.updateProgress(25)
stageLoader.completeStage()
```

### 3. Enhanced Onboarding Hook (`/lib/hooks/useEnhancedOnboarding.ts`)

Combines error handling, retry logic, and loading states:

```typescript
const onboarding = useEnhancedOnboarding({
  maxRetries: 3,
  retryDelay: 1000,
  onSuccess: (result) => console.log('Success:', result),
  onError: (error) => console.error('Error:', error),
  onRetryAttempt: (attempt, error) => console.log(`Retry ${attempt}`)
})

// Submit with automatic error handling and retries
await onboarding.submitOnboarding(data)
```

### 4. UI Components

#### `ErrorDisplay`
Displays user-friendly error messages with retry options:

```typescript
<ErrorDisplay
  error={errorInfo}
  onRetry={canRetry ? handleRetry : undefined}
  onDismiss={handleDismiss}
  compact={false}
/>
```

#### `LoadingIndicator`
Shows loading states with progress and stage information:

```typescript
<LoadingIndicator
  isLoading={true}
  progress={50}
  message="Processing your data..."
  stage="Calculating"
  variant="progress"
/>
```

#### `StageIndicator`
Displays multi-stage process progress:

```typescript
<StageIndicator stages={[
  { key: 'validate', label: 'Validate', completed: true, current: false },
  { key: 'submit', label: 'Submit', completed: false, current: true },
]} />
```

## Error Types and Handling

### Network Errors
- **Detection**: `ERR_NETWORK`, `NETWORK_ERROR`, timeout errors
- **User Message**: "Unable to connect to the server. Please check your internet connection."
- **Retryable**: Yes
- **Retry Strategy**: Exponential backoff with jitter

### CORS Errors
- **Detection**: Status 0 with network error, CORS in message
- **User Message**: "There was a connection issue. Please refresh the page and try again."
- **Retryable**: Yes
- **Retry Strategy**: Limited retries with page refresh suggestion

### Validation Errors (400, 422)
- **Detection**: HTTP 400/422 status codes
- **User Message**: Field-specific validation messages
- **Retryable**: No
- **Action**: Display field errors, allow user to correct input

### Authentication Errors (401, 403)
- **Detection**: HTTP 401/403 status codes
- **User Message**: "Your session has expired. Please log in again."
- **Retryable**: No
- **Action**: Redirect to login

### Server Errors (500, 502, 503, 504)
- **Detection**: HTTP 5xx status codes
- **User Message**: "The server is experiencing issues. Please try again in a few moments."
- **Retryable**: Yes
- **Retry Strategy**: Exponential backoff with longer delays

## Loading Stages

The onboarding process includes these stages:

1. **Validating** (1s): Checking your information...
2. **Submitting** (2s): Sending your data securely...
3. **Calculating** (3s): Calculating your carbon footprint...
4. **Personalizing** (2s): Creating your personalized recommendations...
5. **Finalizing** (1s): Setting up your account...

## Usage in OnboardingWizard

The OnboardingWizard now includes:

1. **Loading Overlay**: Shows during onboarding submission with stage progress
2. **Error Display**: User-friendly error messages with retry options
3. **Retry Information**: Shows retry attempts and progress
4. **Network Status**: Indicates when user is offline
5. **Optimistic Updates**: Immediate UI updates with rollback on failure

## Testing

Use the `ErrorHandlingDemo` component to test different error scenarios:

```typescript
import { ErrorHandlingDemo } from '@/components/onboarding/ErrorHandlingDemo'

// In your development environment
<ErrorHandlingDemo />
```

## Best Practices

1. **Always categorize errors** using `categorizeError()` before displaying
2. **Use appropriate retry strategies** - don't retry validation errors
3. **Provide clear user messages** - avoid technical jargon
4. **Show progress for long operations** - use stage indicators
5. **Handle offline scenarios** - check `navigator.onLine`
6. **Implement optimistic updates** with rollback on failure
7. **Log errors for debugging** while showing user-friendly messages

## Configuration

### Retry Configuration
```typescript
const retryConfig = {
  maxAttempts: 3,        // Maximum retry attempts
  baseDelay: 1000,       // Base delay in milliseconds
  maxDelay: 8000,        // Maximum delay cap
  backoffFactor: 2,      // Exponential backoff multiplier
}
```

### Loading Configuration
```typescript
const loadingConfig = {
  debounceDelay: 200,    // Delay before showing loading
  progressInterval: 50,  // Progress update interval
  stageTransition: 300,  // Stage transition duration
}
```

## Requirements Satisfied

This implementation satisfies the following requirements from the task:

- ✅ **4.1**: User-friendly error messages for network failures
- ✅ **4.2**: Proper handling of 500 errors with retry options
- ✅ **4.3**: Graceful CORS error handling without technical details
- ✅ **4.5**: No infinite redirect loops on authentication errors
- ✅ **Retry mechanisms**: Exponential backoff implementation
- ✅ **Loading states**: Progress indicators during API calls
- ✅ **User experience**: Clear error messages and recovery options