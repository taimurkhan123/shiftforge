import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { RefreshCw, ArrowRight, CheckCircle2, XCircle, ChevronRight } from 'lucide-react'
import { listAdaptations } from '../lib/api'

function formatTime(ts) {
  if (!ts) return '—'
  const d = new Date(ts)
  return d.toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

export default function Adaptations() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [openId, setOpenId] = useState(null)

  const load = async () => {
    try {
      const r = await listAdaptations()
      setItems(r.adaptations || [])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const successCount = items.filter(a => a.result === 'success').length

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto">
      <div className="flex items-start justify-between mb-8">
        <div>
          <div className="text-xs text-accent uppercase tracking-widest font-medium mb-2">
            Adaptation History
          </div>
          <h1 className="text-3xl font-semibold tracking-tight">Adaptations</h1>
          <p className="text-text-secondary mt-1">
            Every successful strategy change. Click any row to inspect the reasoning.
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

      <div className="grid grid-cols-3 gap-4 mb-8">
        <div className="rounded-lg border border-border bg-bg-surface p-4">
          <div className="text-[10px] text-text-muted uppercase tracking-wider mb-1">Total</div>
          <div className="text-2xl font-semibold font-mono">{items.length}</div>
        </div>
        <div className="rounded-lg border border-border bg-bg-surface p-4">
          <div className="text-[10px] text-text-muted uppercase tracking-wider mb-1">Successful</div>
          <div className="text-2xl font-semibold font-mono text-status-success">{successCount}</div>
        </div>
        <div className="rounded-lg border border-border bg-bg-surface p-4">
          <div className="text-[10px] text-text-muted uppercase tracking-wider mb-1">Success Rate</div>
          <div className="text-2xl font-semibold font-mono">
            {items.length ? Math.round((successCount / items.length) * 100) + '%' : '—'}
          </div>
        </div>
      </div>

      {loading ? (
        <div className="text-text-muted">Loading adaptations...</div>
      ) : items.length === 0 ? (
        <div className="rounded-xl border border-dashed border-border bg-bg-surface/50 p-12 text-center text-text-muted">
          No adaptations yet. Run the demo to trigger one.
        </div>
      ) : (
        <div className="rounded-xl border border-border bg-bg-surface overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-bg-elevated border-b border-border">
              <tr className="text-text-muted text-xs uppercase tracking-wider">
                <th className="text-left px-5 py-3 font-medium">Adaptation</th>
                <th className="text-left px-5 py-3 font-medium">Change Type</th>
                <th className="text-left px-5 py-3 font-medium">Strategy</th>
                <th className="text-left px-5 py-3 font-medium">Result</th>
                <th className="text-left px-5 py-3 font-medium">Time</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {items.map(a => (
                <>
                  <tr
                    key={a.adaptation_id}
                    className="border-b border-border/60 last:border-0 hover:bg-bg-elevated/50 transition-colors cursor-pointer"
                    onClick={() => setOpenId(openId === a.adaptation_id ? null : a.adaptation_id)}
                  >
                    <td className="px-5 py-3 font-mono text-xs">{a.adaptation_id}</td>
                    <td className="px-5 py-3 text-text-secondary text-xs">{a.change_type}</td>
                    <td className="px-5 py-3">
                      <span className="font-mono text-xs flex items-center gap-2">
                        {a.from_strategy} <ArrowRight className="w-3 h-3 text-text-muted" /> {a.to_strategy}
                      </span>
                    </td>
                    <td className="px-5 py-3">
                      {a.result === 'success' ? (
                        <span className="inline-flex items-center gap-1.5 text-status-success text-xs">
                          <CheckCircle2 className="w-3.5 h-3.5" /> success
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1.5 text-status-danger text-xs">
                          <XCircle className="w-3.5 h-3.5" /> failed
                        </span>
                      )}
                    </td>
                    <td className="px-5 py-3 text-text-muted text-xs">{formatTime(a.created_at)}</td>
                    <td className="px-5 py-3 text-right">
                      <ChevronRight className={'w-4 h-4 text-text-muted transition-transform ' + (openId === a.adaptation_id ? 'rotate-90' : '')} />
                    </td>
                  </tr>
                  {openId === a.adaptation_id && (
                    <tr key={a.adaptation_id + '-detail'} className="bg-bg-base border-b border-border/60">
                      <td colSpan={6} className="px-5 py-4">
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                          <div>
                            <div className="text-[10px] text-text-muted uppercase tracking-wider mb-2">Diagnosis</div>
                            <pre className="text-xs font-mono bg-bg-surface rounded p-3 border border-border overflow-x-auto">
{JSON.stringify(a.detail?.diagnosis || {}, null, 2)}
                            </pre>
                          </div>
                          <div>
                            <div className="text-[10px] text-text-muted uppercase tracking-wider mb-2">Strategy</div>
                            <pre className="text-xs font-mono bg-bg-surface rounded p-3 border border-border overflow-x-auto">
{JSON.stringify(a.detail?.strategy || {}, null, 2)}
                            </pre>
                          </div>
                        </div>
                        <div className="mt-3">
                          <Link
                            to={'/runs/' + a.run_id}
                            className="text-xs text-accent hover:text-accent-hover"
                          >
                            View full run {a.run_id} →
                          </Link>
                        </div>
                      </td>
                    </tr>
                  )}
                </>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
