interface MemoryFormStubProps {
  locationId: number | null
  onBack: () => void
}

export function MemoryFormStub({ locationId, onBack }: MemoryFormStubProps) {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <button
          onClick={onBack}
          className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 flex items-center gap-1 text-sm font-medium"
        >
          <svg
            className="w-4 h-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15 19l-7-7 7-7"
            />
          </svg>
          Back to history
        </button>
      </div>

      <div className="flex flex-col items-center justify-center py-12 px-4 text-center">
        <div className="w-16 h-16 mb-4 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center">
          <svg
            className="w-8 h-8 text-blue-600 dark:text-blue-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 4v16m8-8H4"
            />
          </svg>
        </div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
          Memory Submission Coming Soon
        </h3>
        <p className="text-sm text-gray-600 dark:text-gray-400 max-w-sm mb-4">
          The memory submission form will be implemented in Task 7.
        </p>
        {locationId && (
          <p className="text-xs text-gray-500 dark:text-gray-500">
            Location ID: {locationId}
          </p>
        )}
      </div>
    </div>
  )
}
