export type ApiErrorCode =
  | 'bad_request'
  | 'unauthorized'
  | 'forbidden'
  | 'not_found'
  | 'conflict'
  | 'validation_error'
  | 'rate_limited'
  | 'server_error'
  | 'network_error'
  | 'timeout'

export interface ApiError {
  code: ApiErrorCode
  message: string
  status: number
  retryAfterMs?: number
}

export function httpStatusToErrorCode(status: number): ApiErrorCode {
  switch (status) {
    case 400:
      return 'bad_request'
    case 401:
      return 'unauthorized'
    case 403:
      return 'forbidden'
    case 404:
      return 'not_found'
    case 409:
      return 'conflict'
    case 422:
      return 'validation_error'
    case 429:
      return 'rate_limited'
    default:
      if (status >= 500) {
        return 'server_error'
      }
      return 'network_error'
  }
}

export function parseRetryAfter(
  retryAfterHeader: string | null
): number | undefined {
  if (!retryAfterHeader) return undefined

  const seconds = parseInt(retryAfterHeader, 10)
  if (!isNaN(seconds)) {
    return seconds * 1000
  }

  const date = new Date(retryAfterHeader)
  if (!isNaN(date.getTime())) {
    return Math.max(0, date.getTime() - Date.now())
  }

  return undefined
}
