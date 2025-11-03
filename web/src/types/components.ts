import { ReactNode } from 'react'
import type { MapBounds, MapInstance } from './map'

export interface MapCanvasProps {
  center: { lat: number; lon: number }
  zoom: number
  onIdle?: (bounds: MapBounds) => void
  onReady?: (map: MapInstance) => void
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
