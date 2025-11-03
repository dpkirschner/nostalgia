import { useEffect, useState } from 'react'
import { useLocationDetail } from '@/hooks/useLocationDetail'
import { logEvent, TelemetryEvents } from '@/lib/telemetry'
import { LocationDetailSkeleton } from './LocationDetailSkeleton'
import { LocationDetailError } from './LocationDetailError'
import { LocationDetailTimeline } from './LocationDetailTimeline'
import { MemoryForm } from './MemoryForm'
import type { ApiError } from '@/types/api'

type DrawerView = 'timeline' | 'memory-form'

interface LocationDetailDrawerProps {
  locationId: number
  view: DrawerView
  onViewChange: (view: DrawerView) => void
}

export function LocationDetailDrawer({
  locationId,
  view,
  onViewChange,
}: LocationDetailDrawerProps) {
  const [loadStartTime] = useState(() => Date.now())
  const { data, isLoading, isFetching, isError, error, refetch } =
    useLocationDetail(locationId)

  useEffect(() => {
    logEvent(TelemetryEvents.DETAIL_OPENED, { location_id: locationId })
  }, [locationId])

  useEffect(() => {
    if (data) {
      const loadTime = Date.now() - loadStartTime
      logEvent(TelemetryEvents.DETAIL_LOADED, {
        location_id: locationId,
        timeline_len: data.timeline.length,
        ms: loadTime,
      })
    }
  }, [data, locationId, loadStartTime])

  useEffect(() => {
    if (isError && error) {
      logEvent(TelemetryEvents.DETAIL_FAILED, {
        location_id: locationId,
        code: (error as ApiError).code,
      })
    }
  }, [isError, error, locationId])

  const handleAddMemory = () => {
    logEvent(TelemetryEvents.CTA_ADD_MEMORY_CLICKED, {
      location_id: locationId,
    })
    onViewChange('memory-form')
  }

  const handleBackToTimeline = () => {
    onViewChange('timeline')
  }

  if (view === 'memory-form') {
    return (
      <MemoryForm locationId={locationId} onBack={handleBackToTimeline} />
    )
  }

  if (isLoading) {
    return <LocationDetailSkeleton />
  }

  if (isError && error) {
    return (
      <LocationDetailError
        error={error as ApiError}
        onRetry={() => refetch()}
        onAddMemory={handleAddMemory}
      />
    )
  }

  if (!data) {
    return null
  }

  const isRefreshing = isFetching && !isLoading

  return (
    <LocationDetailTimeline
      timeline={data.timeline}
      onAddMemory={handleAddMemory}
      isRefreshing={isRefreshing}
    />
  )
}
