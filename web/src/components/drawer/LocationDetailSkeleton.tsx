export function LocationDetailSkeleton() {
  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <div className="h-6 w-3/4 bg-gray-200 dark:bg-gray-800 rounded animate-pulse" />
        <div className="h-4 w-full bg-gray-200 dark:bg-gray-800 rounded animate-pulse" />
      </div>

      <div className="space-y-3">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="h-12 bg-gray-100 dark:bg-gray-800 rounded-lg animate-pulse"
          />
        ))}
      </div>

      <div className="h-10 bg-blue-100 dark:bg-blue-900 rounded-lg animate-pulse" />
    </div>
  )
}
