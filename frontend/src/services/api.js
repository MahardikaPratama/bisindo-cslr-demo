import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const uploadVideo = async (file) => {
  const formData = new FormData()
  formData.append('file', file)
  
  try {
    const response = await apiClient.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  } catch (error) {
    console.error('Upload error:', error)
    throw error
  }
}

export const predict = async (videoId) => {
  try {
    const response = await apiClient.post('/predict', null, {
      params: { video_id: videoId },
    })
    return response.data
  } catch (error) {
    console.error('Prediction error:', error)
    throw error
  }
}

export const checkStatus = async (jobId) => {
  try {
    const response = await apiClient.get(`/status/${jobId}`)
    return response.data
  } catch (error) {
    console.error('Status check error:', error)
    throw error
  }
}

export const getResults = async (videoId) => {
  try {
    const response = await apiClient.get(`/results/${videoId}`)
    return response.data
  } catch (error) {
    console.error('Results retrieval error:', error)
    throw error
  }
}

export const healthCheck = async () => {
  try {
    const response = await apiClient.get('/health')
    return response.data
  } catch (error) {
    console.error('Health check error:', error)
    throw error
  }
}

export default apiClient
