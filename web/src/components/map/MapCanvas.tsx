import { useEffect, useRef, useState } from 'react'
import { Map, NavigationControl, Marker } from 'maplibre-gl'
import type { MapCanvasProps } from '../../types/components'
import type { MapBounds } from '../../types/map'
import { MAP_STYLE_URL, IDLE_DEBOUNCE_MS } from '../../config/map'

export function MapCanvas({ center, zoom, onIdle, onReady }: MapCanvasProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null)
  const mapRef = useRef<Map | null>(null)
  const userMarkerRef = useRef<Marker | null>(null)
  const idleTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const onIdleRef = useRef(onIdle)
  const onReadyRef = useRef(onReady)
  const [isMapReady, setIsMapReady] = useState(false)

  useEffect(() => {
    onIdleRef.current = onIdle
    onReadyRef.current = onReady
  }, [onIdle, onReady])

  useEffect(() => {
    if (!mapContainerRef.current || mapRef.current) return

    const map = new Map({
      container: mapContainerRef.current,
      style: MAP_STYLE_URL,
      center: [center.lon, center.lat],
      zoom: zoom,
      bearing: 0,
      pitch: 0,
      interactive: true,
      bearingSnap: 0,
      pitchWithRotate: false,
      dragRotate: false,
      touchPitch: false,
    })

    map.addControl(
      new NavigationControl({
        showCompass: false,
        showZoom: true,
        visualizePitch: false,
      }),
      'top-right'
    )

    map.on('load', () => {
      setIsMapReady(true)
      onReadyRef.current?.(map)
    })

    const handleIdle = () => {
      if (idleTimeoutRef.current) {
        clearTimeout(idleTimeoutRef.current)
      }

      idleTimeoutRef.current = setTimeout(() => {
        const bounds = map.getBounds()
        const mapBounds: MapBounds = {
          north: bounds.getNorth(),
          south: bounds.getSouth(),
          east: bounds.getEast(),
          west: bounds.getWest(),
        }
        onIdleRef.current?.(mapBounds)
      }, IDLE_DEBOUNCE_MS)
    }

    map.on('idle', handleIdle)

    mapRef.current = map

    return () => {
      if (idleTimeoutRef.current) {
        clearTimeout(idleTimeoutRef.current)
      }
      map.remove()
      mapRef.current = null
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    if (!mapRef.current || !isMapReady) return

    mapRef.current.flyTo({
      center: [center.lon, center.lat],
      zoom: zoom,
      duration: 1000,
      essential: true,
    })
  }, [center.lat, center.lon, zoom, isMapReady])

  useEffect(() => {
    if (!mapRef.current || !isMapReady) return

    if (userMarkerRef.current) {
      userMarkerRef.current.remove()
      userMarkerRef.current = null
    }

    if (center.lat !== 47.6062 || center.lon !== -122.3321) {
      const markerElement = document.createElement('div')
      markerElement.className =
        'w-4 h-4 bg-blue-500 rounded-full border-2 border-white shadow-lg'

      const marker = new Marker({ element: markerElement })
        .setLngLat([center.lon, center.lat])
        .addTo(mapRef.current)

      userMarkerRef.current = marker
    }

    return () => {
      if (userMarkerRef.current) {
        userMarkerRef.current.remove()
        userMarkerRef.current = null
      }
    }
  }, [center.lat, center.lon, isMapReady])

  return <div ref={mapContainerRef} className="absolute inset-0 z-0" />
}
