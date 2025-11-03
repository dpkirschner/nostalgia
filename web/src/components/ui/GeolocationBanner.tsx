import { setOnboardingDismissed } from "../../lib/storage";

interface GeolocationBannerProps {
  onDismiss: () => void;
}

export function GeolocationBanner({ onDismiss }: GeolocationBannerProps) {
  const handleDismiss = () => {
    setOnboardingDismissed();
    onDismiss();
  };

  return (
    <div className="bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 rounded-xl p-4 space-y-3">
      <h3 className="text-lg font-semibold text-blue-900 dark:text-blue-100">
        We use your location to tell you what used to be here.
      </h3>
      <p className="text-sm text-blue-800 dark:text-blue-200">
        It's only used to find nearby places—never stored.
      </p>
      <div className="flex gap-3 pt-2">
        <button
          onClick={handleDismiss}
          className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2"
        >
          OK
        </button>
        <a
          href="https://github.com/yourusername/nostalgia#privacy"
          target="_blank"
          rel="noopener noreferrer"
          className="flex-1 px-4 py-2 bg-white dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 text-blue-600 dark:text-blue-400 border border-blue-200 dark:border-blue-800 rounded-lg font-medium transition-colors text-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2"
        >
          Learn More
        </a>
      </div>
    </div>
  );
}
