import { ReactNode } from 'react'
import type { MapBounds, MapInstance } from './map'
import type { Pin } from './location'

export interface MapCanvasProps {
  center: { lat: number; lon: number }
  zoom: number
  pins?: Pin[]
  onIdle?: (bounds: MapBounds) => void
  onReady?: (map: MapInstance) => void
  onPinClick?: (pin: Pin) => void
}

export interface PrimaryFABProps {
  onPress: () => void
}

export interface BottomDrawerProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  title?: string
  children: ReactNode
}
