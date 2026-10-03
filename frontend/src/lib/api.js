import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
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
