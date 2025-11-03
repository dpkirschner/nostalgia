import { useState, useEffect, type ReactNode } from 'react'
import { MapCanvas } from '../map/MapCanvas'
import { Logo } from '../ui/Logo'
import { PrimaryFAB } from '../ui/PrimaryFAB'
import { BottomDrawer } from '../ui/BottomDrawer'
import { GeolocationBanner } from '../ui/GeolocationBanner'
import { GeolocationButton } from '../map/GeolocationButton'
import { LocationDetailDrawer } from '../drawer/LocationDetailDrawer'
import { useGeolocation } from '../../hooks/useGeolocation'
import { useLocations } from '../../hooks/useLocations'
import { useLocationDetail } from '../../hooks/useLocationDetail'
import { isOnboardingDismissed } from '../../lib/storage'
import { getErrorMessage } from '../../lib/geolocationMessages'
import {
  DEFAULT_CENTER,
  DEFAULT_ZOOM,
  USER_ZOOM,
  MIN_ZOOM_FOR_PINS,
  MAX_PINS_PER_REQUEST,
} from '../../config/map'
import type { MapBounds, MapInstance } from '../../types/map'
import type { Pin } from '../../types/location'

type DrawerView = 'timeline' | 'memory-form'

interface AppLayoutProps {
  drawerContent?: ReactNode
}

export function AppLayout({ drawerContent }: AppLayoutProps) {
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [showBanner, setShowBanner] = useState(false)
  const [bounds, setBounds] = useState<MapBounds | null>(null)
  const [currentZoom, setCurrentZoom] = useState(DEFAULT_ZOOM)
  const [selectedLocationId, setSelectedLocationId] = useState<number | null>(
    null
  )
  const [drawerView, setDrawerView] = useState<DrawerView>('timeline')
  const [mapInstance, setMapInstance] = useState<MapInstance | null>(null)
  const geo = useGeolocation()

  const { data: locationDetail } = useLocationDetail(selectedLocationId)

  const shouldFetchPins = bounds !== null && currentZoom >= MIN_ZOOM_FOR_PINS
  const { data: locationsData } = useLocations(
    shouldFetchPins ? bounds : null,
    MAX_PINS_PER_REQUEST
  )

  useEffect(() => {
    if (geo.consent === 'unset' && !isOnboardingDismissed()) {
      setShowBanner(true)
      setDrawerOpen(true)
    }
  }, [geo.consent])

  const mapCenter = geo.position
    ? { lat: geo.position.lat, lon: geo.position.lon }
    : DEFAULT_CENTER

  const mapZoom = geo.position ? USER_ZOOM : DEFAULT_ZOOM

  const handleBannerDismiss = () => {
    setShowBanner(false)
  }

  const handleMapIdle = (newBounds: MapBounds) => {
    setBounds(newBounds)
  }

  const handlePinClick = (pin: Pin) => {
    setSelectedLocationId(pin.id)
    setDrawerView('timeline')
    setDrawerOpen(true)
  }

  const handleMapReady = (map: MapInstance) => {
    setMapInstance(map)
    setCurrentZoom(map.getZoom())
    map.on('zoomend', () => {
      setCurrentZoom(map.getZoom())
    })
  }

  const handleFABPress = () => {
    setDrawerOpen(true)
  }

  const handleNoDataNearby = () => {
    setSelectedLocationId(null)
    setDrawerView('timeline')
    setDrawerOpen(true)
  }

  const getDrawerTitle = () => {
    if (showBanner) return 'Welcome'
    if (geo.error) return 'Location unavailable'
    if (selectedLocationId && locationDetail) {
      const currentBusiness = locationDetail.timeline.find((t) => t.is_current)
        ?.business_name
      return currentBusiness || 'Unknown here'
    }
    return 'What used to be here?'
  }

  const getDrawerContent = () => {
    if (showBanner) {
      return <GeolocationBanner onDismiss={handleBannerDismiss} />
    }

    if (geo.error) {
      return (
        <div className="space-y-3">
          <p className="text-gray-700 dark:text-gray-300">
            {getErrorMessage(geo.error)}
          </p>
          {geo.error.reason === 'denied' && (
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
      )
    }

    if (selectedLocationId) {
      return (
        <LocationDetailDrawer
          locationId={selectedLocationId}
          view={drawerView}
          onViewChange={setDrawerView}
        />
      )
    }

    return (
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
    )
  }

  return (
    <div className="relative h-screen w-screen overflow-hidden">
      <MapCanvas
        center={mapCenter}
        zoom={mapZoom}
        pins={locationsData?.locations}
        onIdle={handleMapIdle}
        onReady={handleMapReady}
        onPinClick={handlePinClick}
      />

      <Logo />

      <PrimaryFAB
        map={mapInstance}
        userPosition={geo.position}
        pins={locationsData?.locations || []}
        onPress={handleFABPress}
        onPinClick={handlePinClick}
        onNoDataNearby={handleNoDataNearby}
      />

      <GeolocationButton
        onPress={geo.requestLocation}
        isRequesting={geo.isRequesting}
        isDenied={geo.consent === 'denied'}
      />

      <BottomDrawer
        open={drawerOpen}
        onOpenChange={setDrawerOpen}
        title={getDrawerTitle()}
      >
        {getDrawerContent()}
      </BottomDrawer>
    </div>
  )
}
