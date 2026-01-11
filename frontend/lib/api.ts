import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || ''

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
    'x-api-key': API_KEY
  }
})

export const startScraping = async (config: any) => {
  const response = await api.post('/api/scrape', config)
  return response.data
}

export const getJobs = async (params?: any) => {
  const response = await api.get('/api/jobs', { params })
  return response.data
}

export const getStats = async () => {
  const response = await api.get('/api/stats')
  return response.data
}

export const getSettings = async () => {
  const response = await api.get('/api/settings')
  return response.data
}

export const updateSettings = async (key: string, value: any) => {
  const response = await api.post('/api/settings', { key, value })
  return response.data
}

export const updateTinyUrls = async () => {
  const response = await api.post('/api/update-tinyurls')
  return response.data
}

export const getLogs = async (params?: any) => {
  const response = await api.get('/api/logs', { params })
  return response.data
}

export const getSchedule = async () => {
  const response = await api.get('/api/schedule')
  return response.data
}

export const saveSchedule = async (schedule: any) => {
  const response = await api.post('/api/schedule', schedule)
  return response.data
}

export const stopScraping = async () => {
  const response = await api.post('/api/stop-scraping')
  return response.data
}

export const getScrapingStatus = async () => {
  const response = await api.get('/api/scraping-status')
  return response.data
}

export default api
