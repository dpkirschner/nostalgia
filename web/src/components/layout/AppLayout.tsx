import { useState, useEffect, type ReactNode } from "react";
import { MapCanvas } from "../map/MapCanvas";
import { Logo } from "../ui/Logo";
import { PrimaryFAB } from "../ui/PrimaryFAB";
import { BottomDrawer } from "../ui/BottomDrawer";
import { GeolocationBanner } from "../ui/GeolocationBanner";
import { GeolocationButton } from "../map/GeolocationButton";
import { useGeolocation } from "../../hooks/useGeolocation";
import { isOnboardingDismissed } from "../../lib/storage";
import { getErrorMessage } from "../../lib/geolocationMessages";
import { DEFAULT_CENTER, DEFAULT_ZOOM, USER_ZOOM } from "../../config/map";

interface AppLayoutProps {
  drawerContent?: ReactNode;
}

export function AppLayout({ drawerContent }: AppLayoutProps) {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [showBanner, setShowBanner] = useState(false);
  const geo = useGeolocation();

  useEffect(() => {
    if (geo.consent === "unset" && !isOnboardingDismissed()) {
      setShowBanner(true);
      setDrawerOpen(true);
    }
  }, [geo.consent]);

  const mapCenter = geo.position
    ? { lat: geo.position.lat, lon: geo.position.lon }
    : DEFAULT_CENTER;

  const mapZoom = geo.position ? USER_ZOOM : DEFAULT_ZOOM;

  const handleBannerDismiss = () => {
    setShowBanner(false);
  };

  const drawerTitle = showBanner
    ? "Welcome"
    : geo.error
      ? "Location unavailable"
      : "What used to be here?";

  const drawerContentToShow = showBanner ? (
    <GeolocationBanner onDismiss={handleBannerDismiss} />
  ) : geo.error ? (
    <div className="space-y-3">
      <p className="text-gray-700 dark:text-gray-300">
        {getErrorMessage(geo.error)}
      </p>
      {geo.error.reason === "denied" && (
        <div className="text-sm text-gray-600 dark:text-gray-400 bg-gray-100 dark:bg-gray-800 p-3 rounded-lg">
          <p className="font-medium mb-1">To enable location:</p>
          <ol className="list-decimal list-inside space-y-1">
            <li>Click the site settings icon in your browser</li>
            <li>Change location permission to "Allow"</li>
            <li>Click the location button to retry</li>
          </ol>
        </div>
      )}
    </div>
  ) : (
    drawerContent || (
      <div className="space-y-4">
        <p className="text-gray-700 dark:text-gray-300">
          Results will appear here...
        </p>
        <div className="space-y-2">
          {Array.from({ length: 20 }).map((_, i) => (
            <p key={i} className="text-gray-600 dark:text-gray-400">
              Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do
              eiusmod tempor incididunt ut labore et dolore magna aliqua.
            </p>
          ))}
        </div>
      </div>
    )
  );

  return (
    <div className="relative h-screen w-screen overflow-hidden">
      <MapCanvas center={mapCenter} zoom={mapZoom} />

      <Logo />

      <PrimaryFAB onPress={() => setDrawerOpen(true)} />

      <GeolocationButton
        onPress={geo.requestLocation}
        isRequesting={geo.isRequesting}
        isDenied={geo.consent === "denied"}
      />

      <BottomDrawer
        open={drawerOpen}
        onOpenChange={setDrawerOpen}
        title={drawerTitle}
      >
        {drawerContentToShow}
      </BottomDrawer>
    </div>
  );
}
