import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_URL,
  timeout: 60000,
})

export async function getHealth() {
  const r = await api.get('/health')
  return r.data
}

export async function getEnvironment() {
  const r = await api.get('/environment')
  return r.data
}

export async function changeEnvironment() {
  const r = await api.post('/environment/change')
  return r.data
}

export async function runAgent() {
  const r = await api.post('/run')
  return r.data
}

export async function listRuns() {
  const r = await api.get('/runs')
  return r.data
}

export async function getRun(runId) {
  const r = await api.get('/runs/' + runId)
  return r.data
}

export async function listAdaptations() {
  const r = await api.get('/adaptations')
  return r.data
}

export async function listStrategies() {
  const r = await api.get('/strategies')
  return r.data
}

export default api