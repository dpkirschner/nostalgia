import type { ApiError } from '@/types/api'
import { getApiErrorMessage } from '@/lib/apiErrorMessages'

interface LocationDetailErrorProps {
  error: ApiError
  onRetry: () => void
  onAddMemory?: () => void
}

export function LocationDetailError({
  error,
  onRetry,
  onAddMemory,
}: LocationDetailErrorProps) {
  const message = getApiErrorMessage(error)
  const showRetry = error.code !== 'not_found'
  const showAddMemory = error.code === 'not_found' && onAddMemory

  return (
    <div className="flex flex-col items-center justify-center py-8 px-4 text-center">
      <div className="mb-4 text-gray-600 dark:text-gray-400">
        <svg
          className="w-16 h-16 mx-auto mb-3 text-gray-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
          />
        </svg>
        <p className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
          {error.code === 'not_found' && 'No history yet for this spot.'}
          {error.code === 'rate_limited' && "We're busy—try again in a moment."}
          {error.code === 'server_error' && "Couldn't load this location. Retry?"}
          {!['not_found', 'rate_limited', 'server_error'].includes(error.code) &&
            message}
        </p>
        {error.code === 'rate_limited' && error.retryAfterMs && (
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Please wait {Math.ceil(error.retryAfterMs / 1000)} seconds
          </p>
        )}
      </div>

      <div className="flex flex-col gap-2 w-full max-w-xs">
        {showRetry && (
          <button
            onClick={onRetry}
            className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
          >
            Retry
          </button>
        )}
        {showAddMemory && (
          <button
            onClick={onAddMemory}
            className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
          >
            Add what you remember
          </button>
        )}
      </div>
    </div>
  )
}
