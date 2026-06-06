import axios from 'axios'

const API_BASE = 'http://localhost:5000/api/v1'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
})

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Auth
export const authAPI = {
  login: (username, password) => api.post('/auth/login', { username, password }),
  verify: () => api.post('/auth/verify'),
  me: () => api.get('/auth/me'),
}

// Dashboard
export const dashboardAPI = {
  getStatus: () => api.get('/status'),
  getLogs: (lines = 50) => api.get(`/logs?lines=${lines}`),
  getSummary: () => api.get('/summary'),
}

// Workers
export const workersAPI = {
  list: () => api.get('/workers'),
  get: (name) => api.get(`/workers/${name}`),
}

// Commands
export const commandsAPI = {
  startLogin: () => api.post('/commands/start-login'),
  startLoop: () => api.post('/commands/start-loop'),
  stop: () => api.post('/commands/stop'),
  clean: () => api.post('/commands/clean'),
  restart: () => api.post('/commands/restart'),
}

// Files
export const filesAPI = {
  monitor: () => api.get('/files/monitor'),
  getEmails: () => api.get('/files/email'),
  getLinks: () => api.get('/files/link'),
}

// Analytics
export const analyticsAPI = {
  summary: () => api.get('/analytics/summary'),
  completed: () => api.get('/analytics/completed'),
  workerStats: () => api.get('/analytics/worker-stats'),
}

export default api
