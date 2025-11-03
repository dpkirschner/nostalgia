import { useQuery } from '@tanstack/react-query'
import { getLocations } from '../lib/api/locations'
import { QUERY_STALE_TIME } from '../config/api'
import type { MapBounds } from '../types/map'

function roundBounds(bounds: MapBounds, precision: number = 3): MapBounds {
  return {
    north: Number(bounds.north.toFixed(precision)),
    south: Number(bounds.south.toFixed(precision)),
    east: Number(bounds.east.toFixed(precision)),
    west: Number(bounds.west.toFixed(precision)),
  }
}

export function useLocations(bounds: MapBounds | null, limit: number = 300) {
  const roundedBounds = bounds ? roundBounds(bounds) : null

  return useQuery({
    queryKey: ['locations', roundedBounds],
    queryFn: ({ signal }) => {
      if (!roundedBounds) {
        throw new Error('Bounds are required')
      }
      return getLocations(
        {
          west: roundedBounds.west,
          south: roundedBounds.south,
          east: roundedBounds.east,
          north: roundedBounds.north,
          limit,
        },
        signal
      )
    },
    enabled: bounds !== null,
    staleTime: QUERY_STALE_TIME.PINS,
  })
}
