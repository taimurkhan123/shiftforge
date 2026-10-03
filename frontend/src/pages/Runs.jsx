import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { RefreshCw, ChevronRight, Clock } from 'lucide-react'
import { listRuns } from '../lib/api'

const STATUS_BADGE = {
  success: 'bg-status-success/10 text-status-success border-status-success/30',
  change_detected: 'bg-status-warning/10 text-status-warning border-status-warning/30',
  failed: 'bg-status-danger/10 text-status-danger border-status-danger/30',
  pending: 'bg-text-muted/10 text-text-muted border-border',
}

function Badge({ status }) {
  return (
    <span className={'text-[10px] uppercase tracking-wider px-2 py-0.5 rounded border ' + (STATUS_BADGE[status] || STATUS_BADGE.pending)}>
      {status}
    </span>
  )
}

function formatTime(ts) {
  if (!ts) return '—'
  const d = new Date(ts)
  return d.toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

export default function Runs() {
  const [runs, setRuns] = useState([])
  const [loading, setLoading] = useState(true)

  const load = async () => {
    try {
      const r = await listRuns()
      setRuns(r.runs || [])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4 mb-8">
        <div>
          <div className="text-xs text-accent uppercase tracking-widest font-medium mb-2">
            Execution History
          </div>
          <h1 className="text-3xl font-semibold tracking-tight">Runs</h1>
          <p className="text-text-secondary mt-1">
            Every agent run with its full adaptation trace.
          </p>
        </div>
        <button
          onClick={load}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg border border-border hover:bg-bg-elevated text-sm"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh
        </button>
      </div>

      {loading ? (
        <div className="text-text-muted">Loading runs...</div>
      ) : runs.length === 0 ? (
        <div className="rounded-xl border border-dashed border-border bg-bg-surface/50 p-12 text-center text-text-muted">
          No runs yet. Go to Demo Mode and start a run.
        </div>
      ) : (
        <div className="rounded-xl border border-border bg-bg-surface overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-bg-elevated border-b border-border">
              <tr className="text-text-muted text-xs uppercase tracking-wider">
                <th className="text-left px-5 py-3 font-medium">Run ID</th>
                <th className="text-left px-5 py-3 font-medium">Status</th>
                <th className="text-left px-5 py-3 font-medium">Env</th>
                <th className="text-left px-5 py-3 font-medium">Strategy</th>
                <th className="text-left px-5 py-3 font-medium">Time</th>
                <th className="text-left px-5 py-3 font-medium">Created</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {runs.map(r => (
                <tr key={r.run_id} className="border-b border-border/60 last:border-0 hover:bg-bg-elevated/50 transition-colors">
                  <td className="px-5 py-3 font-mono text-xs">{r.run_id}</td>
                  <td className="px-5 py-3"><Badge status={r.status} /></td>
                  <td className="px-5 py-3 font-mono text-xs text-text-secondary">{r.environment_version}</td>
                  <td className="px-5 py-3 font-mono text-xs text-text-secondary">
                    {r.final_strategy_version || r.initial_strategy_version}
                  </td>
                  <td className="px-5 py-3 text-text-secondary text-xs">
                    <span className="inline-flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {r.total_adaptation_ms ? (r.total_adaptation_ms / 1000).toFixed(2) + 's' : '—'}
                    </span>
                  </td>
                  <td className="px-5 py-3 text-text-muted text-xs">{formatTime(r.created_at)}</td>
                  <td className="px-5 py-3 text-right">
                    <Link
                      to={'/runs/' + r.run_id}
                      className="inline-flex items-center gap-1 text-xs text-accent hover:text-accent-hover"
                    >
                      Details <ChevronRight className="w-3 h-3" />
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
