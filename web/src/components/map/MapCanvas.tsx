import type { MapCanvasProps } from "../../types/components";

export function MapCanvas({ onIdle, onReady }: MapCanvasProps) {
  return (
    <div className="absolute inset-0 z-0 bg-gray-100 dark:bg-gray-800">
      <div className="flex items-center justify-center h-full">
        <p className="text-gray-500 dark:text-gray-400 text-lg">
          Map will load here
        </p>
      </div>
    </div>
  );
}
