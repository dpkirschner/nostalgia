import { type PrimaryFABProps } from "../../types/components";
import { cn } from "../../lib/utils";

export function PrimaryFAB({ onPress }: PrimaryFABProps) {
  const handleKeyDown = (e: React.KeyboardEvent<HTMLButtonElement>) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      onPress();
    }
  };

  return (
    <button
      onClick={onPress}
      onKeyDown={handleKeyDown}
      className={cn(
        "fixed bottom-6 left-1/2 -translate-x-1/2 z-10",
        "min-h-[48px] px-8 py-3",
        "bg-blue-600 hover:bg-blue-700 text-white",
        "rounded-full shadow-lg hover:shadow-xl",
        "transition-all duration-150",
        "hover:scale-105 active:scale-95",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2",
        "font-semibold text-base sm:text-lg"
      )}
    >
      What used to be here?
    </button>
  );
}
