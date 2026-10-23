import { createFetch } from '@vueuse/core'

// Create a fetch instance with default configuration for API calls
const apiClient = createFetch({
  baseUrl: import.meta.env.VITE_API_BASE_URL ? `${import.meta.env.VITE_API_BASE_URL}/api/v1` : '/api/v1', // Base URL for API calls
})

export { apiClient }
export default apiClient