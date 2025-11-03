import { cn } from "../../lib/utils";

interface GeolocationButtonProps {
  onPress: () => void;
  isRequesting: boolean;
  isDenied: boolean;
}

export function GeolocationButton({
  onPress,
  isRequesting,
  isDenied,
}: GeolocationButtonProps) {
  return (
    <button
      onClick={onPress}
      disabled={isRequesting}
      className={cn(
        "fixed bottom-24 right-6 z-10",
        "w-12 h-12",
        "bg-white dark:bg-gray-900",
        "border-2 border-gray-300 dark:border-gray-700",
        "rounded-full shadow-lg",
        "flex items-center justify-center",
        "transition-all duration-150",
        "hover:scale-105 hover:shadow-xl",
        "active:scale-95",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2",
        "disabled:opacity-50 disabled:cursor-not-allowed",
        isDenied && "border-red-300 dark:border-red-700"
      )}
      title={
        isDenied
          ? "Location blocked - check settings"
          : isRequesting
            ? "Getting location..."
            : "Use my location"
      }
      aria-label={
        isDenied
          ? "Location blocked"
          : isRequesting
            ? "Getting location"
            : "Use my location"
      }
    >
      {isRequesting ? (
        <svg
          className="w-6 h-6 text-gray-600 dark:text-gray-400 animate-spin"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      ) : (
        <svg
          className={cn(
            "w-6 h-6",
            isDenied
              ? "text-red-600 dark:text-red-400"
              : "text-gray-600 dark:text-gray-400"
          )}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
          />
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
          />
        </svg>
      )}
    </button>
  );
}
