import type { TimelineEntry } from '@/types/location'
import { formatDateRange } from '@/lib/dateUtils'
import { LocationDetailEmpty } from './LocationDetailEmpty'

interface LocationDetailTimelineProps {
  timeline: TimelineEntry[]
  onAddMemory: () => void
}

export function LocationDetailTimeline({
  timeline,
  onAddMemory,
}: LocationDetailTimelineProps) {
  if (timeline.length === 0) {
    return <LocationDetailEmpty onAddMemory={onAddMemory} />
  }

  const displayTimeline = timeline.slice(0, 3)

  return (
    <div className="space-y-6">
      <div className="space-y-3">
        {displayTimeline.map((entry, index) => {
          const dateLabel = formatDateRange(
            entry.start_date,
            entry.end_date,
            entry.is_current
          )

          return (
            <div
              key={index}
              className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <h4 className="font-medium text-gray-900 dark:text-gray-100 truncate">
                    {entry.business_name}
                  </h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    {dateLabel}
                  </p>
                  {entry.category && (
                    <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                      {entry.category}
                    </p>
                  )}
                </div>
                {entry.is_current && (
                  <span className="flex-shrink-0 px-2 py-1 text-xs font-medium text-green-700 dark:text-green-400 bg-green-100 dark:bg-green-900/30 rounded-full">
                    Current
                  </span>
                )}
              </div>
            </div>
          )
        })}
      </div>

      <div className="sticky bottom-0 -mx-4 -mb-4 p-4 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800">
        <button
          onClick={onAddMemory}
          className="w-full px-4 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors mb-2"
        >
          Add what you remember
        </button>
        <button
          disabled
          className="w-full px-4 py-2 text-sm text-gray-400 dark:text-gray-600 hover:text-gray-500 dark:hover:text-gray-500 transition-colors cursor-not-allowed"
        >
          View full history
        </button>
      </div>
    </div>
  )
}
