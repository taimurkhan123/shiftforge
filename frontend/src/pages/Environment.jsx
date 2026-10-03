import { useEffect, useState } from 'react'
import { Server, ArrowRight, AlertTriangle, CheckCircle2, Zap } from 'lucide-react'
import { getEnvironment, changeEnvironment } from '../lib/api'

function JsonBlock({ data, className = '' }) {
  return (
    <pre className={'text-xs font-mono bg-bg-base rounded-lg p-4 border border-border overflow-x-auto ' + className}>
{JSON.stringify(data, null, 2)}
    </pre>
  )
}

function ContractCard({ version, contract, active, accent }) {
  const border = active ? 'border-accent/40' : 'border-border'
  const bg = active ? 'bg-accent/5' : 'bg-bg-surface'
  return (
    <div className={'rounded-xl border ' + border + ' ' + bg + ' p-5'}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <span className={'text-xs font-mono px-2 py-0.5 rounded ' + (active ? 'bg-accent/20 text-accent' : 'bg-bg-elevated text-text-muted')}>
            {version}
          </span>
          <span className="text-sm font-medium">{contract.endpoint}</span>
        </div>
        {active && (
          <span className="text-[10px] uppercase tracking-wider text-accent flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-accent animate-pulse" />
            Active
          </span>
        )}
      </div>
      <dl className="text-xs space-y-2">
        <div className="flex justify-between">
          <dt className="text-text-muted">Method</dt>
          <dd className="font-mono">{contract.method}</dd>
        </div>
        <div className="flex justify-between">
          <dt className="text-text-muted">Temperature field</dt>
          <dd className="font-mono">{contract.temperature_field}</dd>
        </div>
        <div className="flex justify-between">
          <dt className="text-text-muted">Condition field</dt>
          <dd className="font-mono">{contract.condition_field}</dd>
        </div>
      </dl>
    </div>
  )
}

export default function Environment() {
  const [env, setEnv] = useState(null)
  const [loading, setLoading] = useState(false)
  const [justChanged, setJustChanged] = useState(false)

  const load = async () => {
    const e = await getEnvironment()
    setEnv(e)
  }

  useEffect(() => { load() }, [])

  const handleChange = async () => {
    setLoading(true)
    setJustChanged(false)
    try {
      await changeEnvironment()
      await load()
      setJustChanged(true)
      setTimeout(() => setJustChanged(false), 6000)
    } finally {
      setLoading(false)
    }
  }

  if (!env) {
    return <div className="p-8 text-text-muted">Loading environment...</div>
  }

  const v1 = env.all_versions?.v1
  const v2 = env.all_versions?.v2
  const active = env.active_version

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4 mb-8">
        <div>
          <div className="text-xs text-accent uppercase tracking-widest font-medium mb-2">
            Environment Simulator
          </div>
          <h1 className="text-3xl font-semibold tracking-tight">Environment</h1>
          <p className="text-text-secondary mt-1">
            Inspect the tool contract your agent depends on. Break it to trigger adaptation.
          </p>
        </div>
        <button
          onClick={handleChange}
          disabled={loading}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-status-warning/90 hover:bg-status-warning text-black font-medium text-sm disabled:opacity-50 transition-colors"
        >
          <Zap className="w-4 h-4" />
          {loading ? 'Changing…' : 'Simulate Environment Change'}
        </button>
      </div>

      {justChanged && (
        <div className="mb-6 rounded-lg border border-status-warning/40 bg-status-warning/10 text-status-warning px-5 py-4 flex items-center gap-3">
          <AlertTriangle className="w-5 h-5" />
          <div>
            <div className="font-medium">Environment changed</div>
            <div className="text-xs opacity-80">
              Expected contract no longer matches. Agent will detect this on its next run.
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-10">
        <ContractCard
          version="v1"
          contract={v1}
          active={active === 'v1'}
          accent="accent"
        />
        <ContractCard
          version="v2"
          contract={v2}
          active={active === 'v2'}
          accent="warning"
        />
      </div>

      <div className="mb-10">
        <div className="text-xs text-text-muted uppercase tracking-wider mb-3">
          Active Contract (raw)
        </div>
        <JsonBlock data={env.contract} />
      </div>

      <div>
        <div className="text-xs text-text-muted uppercase tracking-wider mb-3">
          Before / After Comparison
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="rounded-xl border border-status-danger/30 bg-status-danger/5 p-5">
            <div className="flex items-center gap-2 mb-4">
              <span className="text-xs font-medium uppercase tracking-wider text-status-danger">
                Before — v1
              </span>
            </div>
            <dl className="text-sm space-y-2">
              <div className="flex justify-between">
                <dt className="text-text-muted">Endpoint</dt>
                <dd className="font-mono">{v1.endpoint}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-text-muted">Temperature</dt>
                <dd className="font-mono">{v1.temperature_field}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-text-muted">Condition</dt>
                <dd className="font-mono">{v1.condition_field}</dd>
              </div>
              <div className="flex justify-between pt-2 border-t border-status-danger/20">
                <dt className="text-text-muted">Status</dt>
                <dd className="text-status-danger text-xs">BREAKS after change</dd>
              </div>
            </dl>
          </div>

          <div className="rounded-xl border border-status-success/30 bg-status-success/5 p-5">
            <div className="flex items-center gap-2 mb-4">
              <span className="text-xs font-medium uppercase tracking-wider text-status-success">
                After — v2 (adapted)
              </span>
            </div>
            <dl className="text-sm space-y-2">
              <div className="flex justify-between">
                <dt className="text-text-muted">Endpoint</dt>
                <dd className="font-mono">{v2.endpoint}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-text-muted">Temperature</dt>
                <dd className="font-mono">{v2.temperature_field}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-text-muted">Condition</dt>
                <dd className="font-mono">{v2.condition_field}</dd>
              </div>
              <div className="flex justify-between pt-2 border-t border-status-success/20">
                <dt className="text-text-muted">Status</dt>
                <dd className="text-status-success text-xs">RECOVERS via adaptation</dd>
              </div>
            </dl>
          </div>
        </div>
      </div>

      <div className="mt-10">
        <div className="text-xs text-text-muted uppercase tracking-wider mb-3">
          Change History
        </div>
        <div className="rounded-xl border border-border bg-bg-surface divide-y divide-border">
          {env.history.slice().reverse().map((v, i) => (
            <div key={i} className="px-5 py-3 flex items-center justify-between text-sm">
              <div className="flex items-center gap-3">
                <span className="text-text-muted text-xs">{env.history.length - i}</span>
                <span className="font-mono">{v}</span>
                <span className="text-text-muted text-xs">
                  {env.all_versions[v]?.endpoint}
                </span>
              </div>
              {v === active && (
                <span className="text-[10px] uppercase tracking-wider text-accent">current</span>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
