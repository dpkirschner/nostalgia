import { cn } from '../../lib/utils'
import { findNearestPin } from '../../lib/mapUtils'
import { logEvent, TelemetryEvents } from '../../lib/telemetry'
import type { MapInstance } from '../../types/map'
import type { Pin } from '../../types/location'
import type { Position } from '../../types/geolocation'

interface PrimaryFABProps {
  map: MapInstance | null
  userPosition: Position | null
  pins: Pin[]
  onPress: () => void
  onPinClick: (pin: Pin) => void
  onNoDataNearby: () => void
}

export function PrimaryFAB({
  map,
  userPosition,
  pins,
  onPress,
  onPinClick,
  onNoDataNearby,
}: PrimaryFABProps) {
  const handleClick = () => {
    if (!userPosition || !map) {
      logEvent(TelemetryEvents.FAB_NEAREST_INVOKED, {
        hadUserLocation: false,
        nearestFound: false,
      })
      onPress()
      return
    }

    const nearestPin = findNearestPin(map, userPosition, pins)

    if (nearestPin) {
      logEvent(TelemetryEvents.FAB_NEAREST_INVOKED, {
        hadUserLocation: true,
        nearestFound: true,
        location_id: nearestPin.id,
      })
      onPinClick(nearestPin)
    } else {
      logEvent(TelemetryEvents.FAB_NEAREST_INVOKED, {
        hadUserLocation: true,
        nearestFound: false,
      })
      onNoDataNearby()
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLButtonElement>) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      handleClick()
    }
  }

  return (
    <button
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      className={cn(
        'fixed bottom-6 left-1/2 -translate-x-1/2 z-10',
        'min-h-[48px] px-8 py-3',
        'bg-blue-600 hover:bg-blue-700 text-white',
        'rounded-full shadow-lg hover:shadow-xl',
        'transition-all duration-150',
        'hover:scale-105 active:scale-95',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2',
        'font-semibold text-base sm:text-lg'
      )}
    >
      What used to be here?
    </button>
  )
}
