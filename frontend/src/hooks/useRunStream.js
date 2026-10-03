import { useEffect, useRef, useState } from 'react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

export function useRunStream(runId) {
  const [events, setEvents] = useState([])
  const esRef = useRef(null)

  useEffect(() => {
    if (!runId) return
    setEvents([])

    const es = new EventSource(API_URL + '/stream/' + runId)
    esRef.current = es

    es.onmessage = (evt) => {
      try {
        const data = JSON.parse(evt.data)
        setEvents(prev => [...prev, data])
        if (data?.data?.final) es.close()
      } catch (err) {
        console.error('SSE parse error', err)
      }
    }

    es.onerror = () => es.close()

    return () => {
      es.close()
      esRef.current = null
    }
  }, [runId])

  return events
}