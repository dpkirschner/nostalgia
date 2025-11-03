import type { MapCanvasProps } from "../../types/components";

export function MapCanvas({
  center,
  zoom,
  onIdle,
  onReady,
}: MapCanvasProps) {
  return (
    <div className="absolute inset-0 z-0 bg-gray-100 dark:bg-gray-800">
      <div className="flex flex-col items-center justify-center h-full gap-2">
        <p className="text-gray-500 dark:text-gray-400 text-lg font-medium">
          Map will load here
        </p>
        <div className="text-sm text-gray-400 dark:text-gray-500 font-mono">
          <p>Center: {center.lat.toFixed(6)}, {center.lon.toFixed(6)}</p>
          <p>Zoom: {zoom}</p>
        </div>
      </div>
    </div>
  );
}
