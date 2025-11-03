export interface Pin {
  id: number
  lat: number
  lon: number
  address: string
  current_business: string | null
  current_category: string | null
}

export interface PinsResponse {
  locations: Pin[]
  count: number
  cursor: string | null
}

export interface TimelineEntry {
  business_name: string
  category: string | null
  start_date: string | null
  end_date: string | null
  is_current: boolean
}

export interface LocationDetail {
  id: number
  lat: number
  lon: number
  address: string
  timeline: TimelineEntry[]
}

export interface LocationsQueryParams {
  west: number
  south: number
  east: number
  north: number
  limit?: number
  cursor?: string
}
