import { useEffect, useState } from 'react'
import { Server, Zap, Play, CheckCircle2, AlertCircle, Loader2, ArrowRight } from 'lucide-react'
import api from '../lib/api'

function ToolCard({ tool, selected, onSelect }) {
  return (
    <button
      onClick={() => onSelect(tool.name)}
      className={
        'text-left rounded-xl border p-4 transition-all ' +
        (selected
          ? 'border-accent/60 bg-accent/5'
          : 'border-border bg-bg-surface hover:border-border/80 hover:bg-bg-elevated')
      }
    >
      <div className="flex items-start justify-between mb-2">
        <div className="font-medium">{tool.display_name}</div>
        <span className={'text-[10px] uppercase tracking-wider px-2 py-0.5 rounded ' +
          (tool.active_version === 'v1'
            ? 'bg-status-success/20 text-status-success'
            : 'bg-status-warning/20 text-status-warning')}>
          {tool.active_version}
        </span>
      </div>
      <div className="text-xs text-text-secondary line-clamp-2">{tool.description}</div>
      <div className="text-[10px] text-text-muted mt-2 font-mono">
        {tool.scenarios.v1.endpoint}
      </div>
    </button>
  )
}

export default function ToolLab() {
  const [tools, setTools] = useState([])
  const [selected, setSelected] = useState(null)
  const [task, setTask] = useState('Complete the requested task using this tool.')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)

  const loadTools = async () => {
    try {
      const r = await api.get('/tools')
      setTools(r.data.tools || [])
      if (!selected && r.data.tools?.length) setSelected(r.data.tools[0].name)
    } catch (e) {
      setError(String(e?.message || e))
    }
  }

  useEffect(() => { loadTools() }, [])

  const currentTool = tools.find(t => t.name === selected)

  const handleChange = async () => {
    if (!selected) return
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      await api.post('/tools/' + selected + '/change')
      await loadTools()
    } catch (e) {
      setError(String(e?.response?.data?.detail || e.message || e))
    } finally {
      setLoading(false)
    }
  }

  const handleRun = async () => {
    if (!selected) return
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const r = await api.post('/tools/' + selected + '/run', { task })
      setResult(r.data)
      await loadTools()
    } catch (e) {
      setError(String(e?.response?.data?.detail || e.message || e))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto">
      <div className="mb-8">
        <div className="text-xs text-accent uppercase tracking-widest font-medium mb-2">
          Multi-Tool Mode
        </div>
        <h1 className="text-3xl font-semibold tracking-tight">Tool Lab</h1>
        <p className="text-text-secondary mt-1">
          Pick a tool, give the agent a task, change the environment, and watch ShiftForge adapt.
        </p>
      </div>

      {/* Tool selector */}
      <div className="mb-8">
        <div className="text-xs text-text-muted uppercase tracking-wider mb-3">1. Select Tool</div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {tools.map(t => (
            <ToolCard key={t.name} tool={t} selected={selected === t.name} onSelect={setSelected} />
          ))}
        </div>
      </div>

      {/* Task input */}
      <div className="mb-8">
        <div className="text-xs text-text-muted uppercase tracking-wider mb-3">2. Enter Task</div>
        <textarea
          value={task}
          onChange={(e) => setTask(e.target.value)}
          rows={2}
          className="w-full rounded-lg border border-border bg-bg-surface px-4 py-3 text-sm text-text-primary focus:border-accent focus:outline-none"
        />
      </div>

      {/* Environment + actions */}
      {currentTool && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <div className="rounded-xl border border-border bg-bg-surface p-5">
            <div className="flex items-center gap-2 mb-4">
              <Server className="w-4 h-4 text-accent" />
              <div className="text-sm font-medium">3. Environment</div>
            </div>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-text-muted">Active version</span>
                <span className={'font-mono ' + (currentTool.active_version === 'v1' ? 'text-status-success' : 'text-status-warning')}>
                  {currentTool.active_version}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-text-muted">Endpoint</span>
                <span className="font-mono">{currentTool.scenarios[currentTool.active_version].endpoint}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-text-muted">Contract</span>
                <span className="font-mono text-[10px]">
                  {Object.entries(currentTool.scenarios[currentTool.active_version].contract)
                    .filter(([k]) => k.endsWith('_field'))
                    .map(([k, v]) => k.replace('_field', '') + '=' + v)
                    .join(', ')}
                </span>
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-border bg-bg-surface p-5">
            <div className="flex items-center gap-2 mb-4">
              <Zap className="w-4 h-4 text-status-warning" />
              <div className="text-sm font-medium">4. Actions</div>
            </div>
            <div className="space-y-3">
              <button
                onClick={handleChange}
                disabled={loading}
                className="w-full inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-status-warning/90 hover:bg-status-warning text-black font-medium text-sm disabled:opacity-50 transition-colors"
              >
                <Zap className="w-4 h-4" />
                Simulate Environment Change
              </button>
              <button
                onClick={handleRun}
                disabled={loading}
                className="w-full inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-accent hover:bg-accent-hover text-white font-medium text-sm disabled:opacity-50 transition-colors"
              >
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
                {loading ? 'Running…' : 'Run Agent'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="mb-6 rounded-lg border border-status-danger/40 bg-status-danger/10 text-status-danger px-4 py-3 text-sm flex items-start gap-2">
          <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
          <div>{error}</div>
        </div>
      )}

      {/* Result */}
      {result && (
        <div className="space-y-4">
          <div className={
            'rounded-lg border px-5 py-4 flex items-center gap-3 ' +
            (result.status === 'success'
              ? 'border-status-success/40 bg-status-success/10 text-status-success'
              : 'border-status-danger/40 bg-status-danger/10 text-status-danger')
          }>
            {result.status === 'success'
              ? <CheckCircle2 className="w-5 h-5" />
              : <AlertCircle className="w-5 h-5" />}
            <div>
              <div className="font-medium">
                {result.status === 'success' ? 'Task Completed' : 'Task Failed'}
              </div>
              <div className="text-xs opacity-80">
                Run {result.run_id} · {result.total_adaptation_ms ? (result.total_adaptation_ms / 1000).toFixed(2) + 's' : '—'}
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-border bg-bg-surface overflow-hidden">
            <div className="px-5 py-3 border-b border-border text-xs text-text-muted uppercase tracking-wider">
              Adaptation Trace
            </div>
            <div className="divide-y divide-border/60">
              {result.steps.map((s, i) => (
                <div key={i} className="px-5 py-3 flex items-start gap-3">
                  <span className={
                    'w-2 h-2 rounded-full mt-1.5 shrink-0 ' +
                    (s.status === 'success' ? 'bg-status-success' :
                     s.status === 'failed' ? 'bg-status-danger' :
                     s.status === 'warning' ? 'bg-status-warning' : 'bg-accent')
                  } />
                  <div className="flex-1 min-w-0">
                    <div className="text-xs uppercase tracking-wider text-text-muted font-mono mb-0.5">
                      {s.stage}
                    </div>
                    <div className="text-sm">{s.message}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-xl border border-border bg-bg-surface p-5">
            <div className="text-xs text-text-muted uppercase tracking-wider mb-2">Final Result</div>
            <pre className="text-xs font-mono bg-bg-base rounded p-3 border border-border overflow-x-auto">
{JSON.stringify(result.result, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  )
}
