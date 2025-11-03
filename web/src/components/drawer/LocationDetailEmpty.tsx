interface LocationDetailEmptyProps {
  onAddMemory: () => void
}

export function LocationDetailEmpty({ onAddMemory }: LocationDetailEmptyProps) {
  return (
    <div className="flex flex-col items-center justify-center py-8 px-4 text-center">
      <div className="mb-6">
        <svg
          className="w-20 h-20 mx-auto mb-4 text-gray-300 dark:text-gray-700"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          />
        </svg>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
          No data yet here
        </h3>
        <p className="text-sm text-gray-600 dark:text-gray-400 max-w-sm">
          Be the first to share what used to be at this location. Your
          contribution helps preserve neighborhood history.
        </p>
      </div>

      <button
        onClick={onAddMemory}
        className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
      >
        Add what you remember
      </button>
    </div>
  )
}
