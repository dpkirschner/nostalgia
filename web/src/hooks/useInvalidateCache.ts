import { useQueryClient } from '@tanstack/react-query'

export function useInvalidateCache() {
  const queryClient = useQueryClient()

  const invalidateLocationDetail = async (locationId: number) => {
    await queryClient.invalidateQueries({
      queryKey: ['location', locationId],
      exact: true,
    })

    if (import.meta.env.DEV) {
      console.log('[Cache] Invalidated location detail:', locationId)
    }
  }

  const invalidateAllLocationDetails = async () => {
    await queryClient.invalidateQueries({
      queryKey: ['location'],
    })

    if (import.meta.env.DEV) {
      console.log('[Cache] Invalidated all location details')
    }
  }

  const invalidateBboxQueries = async () => {
    await queryClient.invalidateQueries({
      queryKey: ['locations'],
    })

    if (import.meta.env.DEV) {
      console.log('[Cache] Invalidated all bbox queries')
    }
  }

  const invalidateAll = async () => {
    await queryClient.invalidateQueries()

    if (import.meta.env.DEV) {
      console.log('[Cache] Invalidated entire cache')
    }
  }

  return {
    invalidateLocationDetail,
    invalidateAllLocationDetails,
    invalidateBboxQueries,
    invalidateAll,
  }
}
