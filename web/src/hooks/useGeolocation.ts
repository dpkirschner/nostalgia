import { useState, useEffect, useCallback, useRef } from 'react'
import {
  GEO_TIMEOUT_MS,
  GEO_MAX_AGE_MS,
  GEO_HIGH_ACCURACY,
} from '../config/map'
import {
  getStoredConsent,
  setStoredConsent,
  getLastPosition,
  setLastPosition,
} from '../lib/storage'
import type {
  GeolocationState,
  Position,
  GeolocationError,
  ConsentState,
  GeolocationResult,
} from '../types/geolocation'

function isSecureContext(): boolean {
  if (typeof window === 'undefined') return false
  return (
    window.location.protocol === 'https:' ||
    window.location.hostname === 'localhost' ||
    window.location.hostname === '127.0.0.1'
  )
}

export function useGeolocation(autoRequest: boolean = false): GeolocationResult {
  const [state, setState] = useState<GeolocationState>('idle')
  const [position, setPosition] = useState<Position | null>(null)
  const [error, setError] = useState<GeolocationError | null>(null)
  const [consent, setConsent] = useState<ConsentState>('unset')
  const hasInitialized = useRef(false)

  const handleSuccess = useCallback((geoPosition: GeolocationPosition) => {
    const newPosition: Position = {
      lat: geoPosition.coords.latitude,
      lon: geoPosition.coords.longitude,
      ts: Date.now(),
      accuracy: geoPosition.coords.accuracy,
    }

    console.log(
      `[Geo] Success: {lat: ${newPosition.lat.toFixed(6)}, lon: ${newPosition.lon.toFixed(6)}, accuracy: ${newPosition.accuracy}m}`
    )

    setPosition(newPosition)
    setLastPosition(newPosition)
    setConsent('granted')
    setStoredConsent('granted')
    setState('granted')
    setError(null)
  }, [])

  const handleError = useCallback((geoError: GeolocationPositionError) => {
    let errorReason: GeolocationError['reason']
    let errorMessage: string

    switch (geoError.code) {
      case geoError.PERMISSION_DENIED:
        errorReason = 'denied'
        errorMessage = 'User denied geolocation permission'
        setConsent('denied')
        setStoredConsent('denied')
        break
      case geoError.TIMEOUT:
        errorReason = 'timeout'
        errorMessage = 'Geolocation request timed out'
        break
      case geoError.POSITION_UNAVAILABLE:
      default:
        errorReason = 'position_unavailable'
        errorMessage = 'Position unavailable'
        break
    }

    console.log(`[Geo] Failed: {reason: ${errorReason}}`)

    setError({ reason: errorReason, message: errorMessage })
    setState('error')
  }, [])

  const requestLocation = useCallback(() => {
    if (!isSecureContext()) {
      console.log('[Geo] Failed: {reason: insecure_origin}')
      setError({
        reason: 'insecure_origin',
        message: 'Geolocation requires HTTPS or localhost',
      })
      setState('error')
      return
    }

    if (!navigator.geolocation) {
      console.log('[Geo] Failed: {reason: position_unavailable}')
      setError({
        reason: 'position_unavailable',
        message: 'Geolocation not supported',
      })
      setState('error')
      return
    }

    console.log('[Geo] Request started')
    setState('requesting')
    setError(null)

    navigator.geolocation.getCurrentPosition(handleSuccess, handleError, {
      enableHighAccuracy: GEO_HIGH_ACCURACY,
      timeout: GEO_TIMEOUT_MS,
      maximumAge: GEO_MAX_AGE_MS,
    })
  }, [handleSuccess, handleError])

  const resetConsent = useCallback(() => {
    setStoredConsent('unset')
    setConsent('unset')
    setState('idle')
    setError(null)
  }, [])

  useEffect(() => {
    if (hasInitialized.current) return
    hasInitialized.current = true

    const storedConsent = getStoredConsent()
    setConsent(storedConsent)

    if (storedConsent === 'granted') {
      const lastPos = getLastPosition()
      if (lastPos) {
        console.log(
          `[Geo] Using cached position: {lat: ${lastPos.lat.toFixed(6)}, lon: ${lastPos.lon.toFixed(6)}}`
        )
        setPosition(lastPos)
        setState('granted')
      }

      if (autoRequest) {
        requestLocation()
      }
    } else if (storedConsent === 'denied') {
      console.log('[Geo] Consent previously denied, skipping request')
      setState('denied')
    }
  }, [autoRequest, requestLocation])

  return {
    state,
    position,
    error,
    consent,
    isRequesting: state === 'requesting',
    requestLocation,
    resetConsent,
  }
}
