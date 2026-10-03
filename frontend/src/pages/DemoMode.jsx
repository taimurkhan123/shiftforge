import { useState } from 'react'
import { PlayCircle, RotateCcw, CheckCircle2, AlertCircle } from 'lucide-react'
import WorkflowDiagram from '../components/WorkflowDiagram'
import AdaptationConsole from '../components/AdaptationConsole'
import { initialNodeStatus, STAGE_TO_NODE } from '../lib/workflow'
import { changeEnvironment, runAgent, getEnvironment } from '../lib/api'
import { useRunStream } from '../hooks/useRunStream'

export default function DemoMode() {
  const [statuses, setStatuses] = useState(initialNodeStatus())
  const [phase, setPhase] = useState('idle')
  const [runId, setRunId] = useState(null)
  const [finalRun, setFinalRun] = useState(null)
  const [error, setError] = useState(null)

  const events = useRunStream(runId)

  // Apply events -> node statuses
  useState(() => {})
  const applyEvent = (evt) => {
    const node = STAGE_TO_NODE[evt.stage]
    if (node) {
      setStatuses(prev => ({ ...prev, [node]: evt.status }))
    }
  }
  // We derive statuses from events on the fly
  // (simpler than threading into SSE)
  // To do that we mirror into state via useEffect-like logic below

  const startDemo = async () => {
    setError(null)
    setFinalRun(null)
    setRunId(null)
    setStatuses(initialNodeStatus())
    setPhase('starting')

    try {
      // 1. Ensure v1
      const env = await getEnvironment()
      if (env.active_version !== 'v1') {
        await changeEnvironment()
      }

      // 2. Break the environment
      setPhase('breaking')
      await changeEnvironment()

      // 3. Kick off run (this returns the full trace after the pipeline completes)
      setPhase('running')
      const newRunId = 'SF-DEMO-' + Math.random().toString(36).slice(2, 8).toUpperCase()
      setRunId(newRunId)

      // Note: /api/run generates its own run_id server-side.
      // We'll subscribe AFTER we know the real one. For now, mark running.
      setPhase('awaiting')

      const result = await runAgent()
      setFinalRun(result)
      setRunId(result.run_id)

      // Mark final node statuses from the completed run steps
      const finalStatuses = initialNodeStatus()
      for (const step of result.steps || []) {
        const node = STAGE_TO_NODE[step.stage]
        if (node) {
          // failed monitor step gets 'failed', later success overrides
          if (step.status === 'failed' && node === 'monitor') {
            finalStatuses[node] = 'failed'
          } else {
            finalStatuses[node] = step.status
          }
        }
      }
      if (result.status === 'success') finalStatuses.complete = 'success'
      setStatuses(finalStatuses)
      setPhase('done')
    } catch (e) {
      console.error(e)
      setError(String(e?.response?.data?.detail || e.message || e))
      setPhase('error')
    }
  }

  // Derive node statuses from live events while running
  const derivedStatuses = { ...statuses }
  for (const e of events) {
    const node = STAGE_TO_NODE[e.stage]
    if (!node) continue
    if (e.status === 'failed' && node === 'monitor' && derivedStatuses.monitor !== 'failed') {
      derivedStatuses.monitor = 'failed'
    } else {
      derivedStatuses[node] = e.status
    }
  }

  const reset = () => {
    setStatuses(initialNodeStatus())
    setPhase('idle')
    setRunId(null)
    setFinalRun(null)
    setError(null)
  }

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4 mb-8">
        <div>
          <div className="text-xs text-accent uppercase tracking-widest font-medium mb-2">
            Live Demonstration
          </div>
          <h1 className="text-3xl font-semibold tracking-tight">Demo Mode</h1>
          <p className="text-text-secondary mt-1">
            Break the environment. Watch the agent adapt. No human intervention.
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={reset}
            disabled={phase === 'running' || phase === 'awaiting'}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg border border-border hover:bg-bg-elevated disabled:opacity-50 text-sm"
          >
            <RotateCcw className="w-4 h-4" />
            Reset
          </button>
          <button
            onClick={startDemo}
            disabled={phase === 'running' || phase === 'awaiting'}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-accent hover:bg-accent-hover disabled:opacity-50 text-white text-sm font-medium"
          >
            <PlayCircle className="w-4 h-4" />
            {phase === 'running' || phase === 'awaiting' ? 'Running…' : 'START LIVE DEMO'}
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-6 rounded-lg border border-status-danger/40 bg-status-danger/10 text-status-danger px-4 py-3 text-sm flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          {error}
        </div>
      )}

      {finalRun && finalRun.status === 'success' && (
        <div className="mb-6 rounded-lg border border-status-success/40 bg-status-success/10 text-status-success px-5 py-4 flex items-center gap-3">
          <CheckCircle2 className="w-5 h-5" />
          <div>
            <div className="font-medium">Agent Adapted</div>
            <div className="text-xs opacity-80">
              Original task completed. Strategy: {finalRun.final_strategy_version || '—'} ·
              {finalRun.total_adaptation_ms ? ' ' + (finalRun.total_adaptation_ms / 1000).toFixed(2) + 's' : ''}
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        <div className="lg:col-span-3 rounded-xl border border-border bg-bg-surface p-4">
          <div className="text-xs text-text-muted uppercase tracking-wider mb-3 px-1">
            Agent Workflow
          </div>
          <WorkflowDiagram statuses={derivedStatuses} />
        </div>

        <div className="lg:col-span-2 space-y-4">
          <div>
            <div className="text-xs text-text-muted uppercase tracking-wider mb-3 px-1">
              Adaptation Console
            </div>
            <AdaptationConsole events={events} />
          </div>

          {finalRun && (
            <div className="rounded-xl border border-border bg-bg-surface p-4">
              <div className="text-xs text-text-muted uppercase tracking-wider mb-3">
                Run Summary
              </div>
              <dl className="text-sm space-y-2">
                <div className="flex justify-between">
                  <dt className="text-text-muted">Run ID</dt>
                  <dd className="font-mono text-xs">{finalRun.run_id}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-text-muted">Status</dt>
                  <dd className="text-status-success uppercase text-xs">{finalRun.status}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-text-muted">Strategy</dt>
                  <dd className="font-mono text-xs">{finalRun.final_strategy_version || '—'}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-text-muted">Adaptation Time</dt>
                  <dd className="font-mono text-xs">
                    {finalRun.total_adaptation_ms ? (finalRun.total_adaptation_ms / 1000).toFixed(2) + 's' : '—'}
                  </dd>
                </div>
              </dl>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
