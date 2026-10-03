import { useEffect, useRef } from 'react'

function formatTime(ts) {
  if (!ts) return '--:--:--'
  const d = new Date(ts)
  return d.toTimeString().slice(0, 8)
}

const STATUS_COLORS = {
  running: 'text-accent',
  success: 'text-status-success',
  warning: 'text-status-warning',
  failed:  'text-status-danger',
}

export default function AdaptationConsole({ events = [] }) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [events.length])

  return (
    <div className="rounded-xl border border-border bg-bg-base">
      <div className="px-4 py-3 border-b border-border flex items-center gap-2">
        <div className="flex gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-status-danger/70" />
          <span className="w-2.5 h-2.5 rounded-full bg-status-warning/70" />
          <span className="w-2.5 h-2.5 rounded-full bg-status-success/70" />
        </div>
        <div className="text-xs text-text-muted ml-2 font-mono">adaptation.log</div>
        <div className="ml-auto text-xs text-text-muted font-mono">
          {events.length} events
        </div>
      </div>
      <div className="p-4 h-[420px] overflow-y-auto font-mono text-xs space-y-1">
        {events.length === 0 && (
          <div className="text-text-muted">
            <span className="text-accent">$</span> awaiting run...
            <span className="inline-block w-2 h-4 bg-accent/50 ml-1 align-middle animate-pulse" />
          </div>
        )}
        {events.map((e, i) => (
          <div key={i} className="flex gap-3 leading-relaxed">
            <span className="text-text-muted shrink-0">[{formatTime(e.timestamp)}]</span>
            <span className={STATUS_COLORS[e.status] || 'text-text-secondary'}>
              [{e.stage}] {e.message}
            </span>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
    </div>
  )
}
