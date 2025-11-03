import type { Map as MapLibreMap } from 'maplibre-gl'

export interface MapBounds {
  north: number
  south: number
  east: number
  west: number
}

export type MapInstance = MapLibreMap

export { Map as MapLibreMap, LngLatBounds, Marker } from 'maplibre-gl'
