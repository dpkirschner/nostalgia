import { useEffect, useRef, useState } from 'react'
import { Map, NavigationControl, Marker, type MapMouseEvent } from 'maplibre-gl'
import type { MapCanvasProps } from '../../types/components'
import type { MapBounds } from '../../types/map'
import type { Pin } from '../../types/location'
import {
  MAP_STYLE_URL,
  IDLE_DEBOUNCE_MS,
  PIN_COLOR_KNOWN,
  PIN_COLOR_UNKNOWN,
  PIN_RADIUS_KNOWN,
  PIN_RADIUS_UNKNOWN,
  PIN_STROKE_WIDTH,
} from '../../config/map'

function pinsToGeoJSON(pins: Pin[]): GeoJSON.FeatureCollection {
  return {
    type: 'FeatureCollection',
    features: pins.map((pin) => ({
      type: 'Feature',
      geometry: {
        type: 'Point',
        coordinates: [pin.lon, pin.lat],
      },
      properties: {
        id: pin.id,
        address: pin.address,
        current_business: pin.current_business,
        current_category: pin.current_category,
      },
    })),
  }
}

export function MapCanvas({
  center,
  zoom,
  pins = [],
  onIdle,
  onReady,
  onPinClick,
}: MapCanvasProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null)
  const mapRef = useRef<Map | null>(null)
  const userMarkerRef = useRef<Marker | null>(null)
  const idleTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const onIdleRef = useRef(onIdle)
  const onReadyRef = useRef(onReady)
  const onPinClickRef = useRef(onPinClick)
  const [isMapReady, setIsMapReady] = useState(false)

  useEffect(() => {
    onIdleRef.current = onIdle
    onReadyRef.current = onReady
    onPinClickRef.current = onPinClick
  }, [onIdle, onReady, onPinClick])

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
      map.addSource('locations', {
        type: 'geojson',
        data: pinsToGeoJSON([]),
      })

      map.addLayer({
        id: 'locations-known',
        type: 'circle',
        source: 'locations',
        filter: ['!=', ['get', 'current_business'], null],
        paint: {
          'circle-radius': PIN_RADIUS_KNOWN,
          'circle-color': PIN_COLOR_KNOWN,
          'circle-stroke-width': 1,
          'circle-stroke-color': '#ffffff',
        },
      })

      map.addLayer({
        id: 'locations-unknown',
        type: 'circle',
        source: 'locations',
        filter: ['==', ['get', 'current_business'], null],
        paint: {
          'circle-radius': PIN_RADIUS_UNKNOWN,
          'circle-color': '#ffffff',
          'circle-stroke-width': PIN_STROKE_WIDTH,
          'circle-stroke-color': PIN_COLOR_UNKNOWN,
        },
      })

      const handlePinClick = (e: MapMouseEvent) => {
        const features = e.features
        if (features && features.length > 0) {
          const props = features[0].properties
          const pin: Pin = {
            id: props.id,
            lat: features[0].geometry.coordinates[1],
            lon: features[0].geometry.coordinates[0],
            address: props.address,
            current_business: props.current_business,
            current_category: props.current_category,
          }
          onPinClickRef.current?.(pin)
        }
      }

      map.on('click', 'locations-known', handlePinClick)
      map.on('click', 'locations-unknown', handlePinClick)

      map.on('mouseenter', 'locations-known', () => {
        map.getCanvas().style.cursor = 'pointer'
      })
      map.on('mouseleave', 'locations-known', () => {
        map.getCanvas().style.cursor = ''
      })
      map.on('mouseenter', 'locations-unknown', () => {
        map.getCanvas().style.cursor = 'pointer'
      })
      map.on('mouseleave', 'locations-unknown', () => {
        map.getCanvas().style.cursor = ''
      })

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

  useEffect(() => {
    if (!mapRef.current || !isMapReady) return

    const source = mapRef.current.getSource('locations')
    if (source && source.type === 'geojson') {
      source.setData(pinsToGeoJSON(pins))
    }
  }, [pins, isMapReady])

  return <div ref={mapContainerRef} className="absolute inset-0 z-0" />
}
