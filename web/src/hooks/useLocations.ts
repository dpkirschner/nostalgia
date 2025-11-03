import { useQuery } from '@tanstack/react-query'
import { useEffect, useRef } from 'react'
import { getLocations } from '../lib/api/locations'
import { QUERY_STALE_TIME } from '../config/api'
import { roundBounds, pinsHaveChanged } from '../lib/cache/bboxUtils'
import { bboxCacheLimiter } from '../lib/cache/bboxCacheLimiter'
import type { MapBounds } from '../types/map'
import type { Pin } from '../types/location'

export function useLocations(bounds: MapBounds | null, limit: number = 300) {
  const roundedBounds = bounds ? roundBounds(bounds) : null
  const queryKey = ['locations', roundedBounds]
  const previousPins = useRef<Pin[]>()

  const query = useQuery({
    queryKey,
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
    select: (data) => {
      const pins = data.locations
      const hasChanged = pinsHaveChanged(previousPins.current, pins)

      if (hasChanged) {
        previousPins.current = pins
      }

      return data
    },
  })

  useEffect(() => {
    if (query.isSuccess && roundedBounds) {
      bboxCacheLimiter.trackBboxQuery(queryKey)
    }
  }, [query.isSuccess, queryKey])

  return query
}
