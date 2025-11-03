export type ConsentState = 'granted' | 'denied' | 'unset'

export type GeolocationState =
  | 'idle'
  | 'requesting'
  | 'granted'
  | 'denied'
  | 'error'

export interface Position {
  lat: number
  lon: number
  ts: number
  accuracy?: number
}

export type ErrorReason =
  | 'timeout'
  | 'denied'
  | 'position_unavailable'
  | 'insecure_origin'

export interface GeolocationError {
  reason: ErrorReason
  message: string
}

export interface GeolocationResult {
  state: GeolocationState
  position: Position | null
  error: GeolocationError | null
  consent: ConsentState
  isRequesting: boolean
  requestLocation: () => void
  resetConsent: () => void
}
