import { useMutation, useQueryClient } from '@tanstack/react-query'
import { submitMemory } from '@/lib/api/memories'
import type { MemorySubmissionData } from '@/types/memory'

export function useSubmitMemory() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: MemorySubmissionData) => submitMemory(data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: ['location', variables.location_id],
      })
    },
  })
}
