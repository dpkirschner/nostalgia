const apiBaseUrl = import.meta.env.VITE_API_BASE_URL

if (!apiBaseUrl || apiBaseUrl.trim() === '') {
  throw new Error(
    'VITE_API_BASE_URL is not defined. Please set it in your .env file.'
  )
}

export const API_BASE_URL: string = apiBaseUrl
