import { useQuery } from '@tanstack/react-query'
import { getLocationDetail } from '../lib/api/locations'
import { QUERY_STALE_TIME } from '../config/api'

export function useLocationDetail(locationId: number | null) {
  return useQuery({
    queryKey: ['location', locationId],
    queryFn: ({ signal }) => {
      if (locationId === null) {
        throw new Error('Location ID is required')
      }
      return getLocationDetail(locationId, signal)
    },
    enabled: locationId !== null,
    staleTime: QUERY_STALE_TIME.LOCATION_DETAIL,
  })
}
