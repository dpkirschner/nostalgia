export const API_TIMEOUT_MS = 8000

export const CACHE_TTL = {
  PINS_MS: 60 * 1000,
  LOCATION_DETAIL_MS: 15 * 60 * 1000,
} as const

export const RETRY_CONFIG = {
  MAX_RETRIES: 1,
  RETRY_DELAY_MS: 300,
  RETRY_STATUS_CODES: [408, 429, 500, 502, 503, 504],
} as const

export const QUERY_STALE_TIME = {
  PINS: CACHE_TTL.PINS_MS,
  LOCATION_DETAIL: CACHE_TTL.LOCATION_DETAIL_MS,
} as const

export const QUERY_GC_TIME_MS = 5 * 60 * 1000

export const BBOX_CACHE = {
  MAX_ENTRIES: 3,
  COORDINATE_PRECISION: 5,
  THROTTLE_MS: 1500,
} as const

export const CACHE_PERSISTENCE = {
  INDEXEDDB_NAME: 'nostalgia-query-cache',
  MAX_AGE_MS: 24 * 60 * 60 * 1000,
  BUSTER: 'v1',
} as const

export const CACHE_KEYS = {
  locations: (bounds: { west: number; south: number; east: number; north: number }) =>
    `bbox:${bounds.west.toFixed(BBOX_CACHE.COORDINATE_PRECISION)}:${bounds.south.toFixed(BBOX_CACHE.COORDINATE_PRECISION)}:${bounds.east.toFixed(BBOX_CACHE.COORDINATE_PRECISION)}:${bounds.north.toFixed(BBOX_CACHE.COORDINATE_PRECISION)}`,
  locationDetail: (locationId: number) => `loc:${locationId}`,
} as const
