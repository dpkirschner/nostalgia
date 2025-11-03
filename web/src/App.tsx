import { useEffect } from 'react'
import { API_BASE_URL } from './config/env'

function App() {
  useEffect(() => {
    console.log('API_BASE_URL:', API_BASE_URL)
  }, [])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <h1 className="text-4xl font-bold text-gray-900">Nostalgia</h1>
    </div>
  )
}

export default App
