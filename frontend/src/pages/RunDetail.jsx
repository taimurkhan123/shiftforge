import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, CheckCircle2, AlertCircle, Circle } from 'lucide-react'
import { getRun } from '../lib/api'
import StrategyDiff from '../components/StrategyDiff'

const STEP_STATUS_ICON = {
  success: <CheckCircle2 className="w-4 h-4 text-status-success" />,
  failed:  <AlertCircle  className="w-4 h-4 text-status-danger" />,
  running: <Circle       className="w-4 h-4 text-accent animate-pulse" />,
  warning: <AlertCircle  className="w-4 h-4 text-status-warning" />,
}

function formatTime(ts) {
  if (!ts) return '—'
  return new Date(ts).toLocaleString()
}

export default function RunDetail() {
  const { runId } = useParams()
  const [run, setRun] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    const load = async () => {
      try {
        const r = await getRun(runId)
        setRun(r)
      } catch (e) {
        setError('Run ' + runId + ' not found.')
      }
    }
    load()
  }, [runId])

  if (error) {
    return (
      <div className="p-8">
        <Link to="/runs" className="inline-flex items-center gap-2 text-sm text-text-secondary hover:text-accent mb-6">
          <ArrowLeft className="w-4 h-4" /> Back to runs
        </Link>
        <div className="rounded-xl border border-status-danger/40 bg-status-danger/10 text-status-danger p-5">
          {error}
        </div>
      </div>
    )
  }

  if (!run) {
    return <div className="p-8 text-text-muted">Loading run...</div>
  }

  // Extract diagnosis + strategy from steps (from stored step data)
  const diagnosisStep = run.steps.find(s => s.stage === 'diagnosis')
  const strategyStep  = run.steps.find(s => s.stage === 'strategy')
  const validationStep = run.steps.find(s => s.stage === 'validation')

  const before = {
    endpoint: '/api/weather',
    temperature_field: 'temperature',
    condition_field: 'condition',
  }
  const after = strategyStep?.data || {
    endpoint: '/api/forecast',
    temperature_field: 'temp_c',
    condition_field: 'weather',
  }

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <Link to="/runs" className="inline-flex items-center gap-2 text-sm text-text-secondary hover:text-accent mb-6">
        <ArrowLeft className="w-4 h-4" /> Back to runs
      </Link>

      <div className="mb-8">
        <div className="text-xs text-accent uppercase tracking-widest font-medium mb-2">
          Run Detail
        </div>
        <h1 className="text-3xl font-semibold tracking-tight font-mono">{run.run_id}</h1>
        <p className="text-text-secondary mt-1">{run.task}</p>
      </div>

      {/* Summary grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div className="rounded-lg border border-border bg-bg-surface p-4">
          <div className="text-[10px] text-text-muted uppercase tracking-wider mb-1">Status</div>
          <div className="text-sm font-medium uppercase tracking-wider text-status-success">{run.status}</div>
        </div>
        <div className="rounded-lg border border-border bg-bg-surface p-4">
          <div className="text-[10px] text-text-muted uppercase tracking-wider mb-1">Env</div>
          <div className="text-sm font-mono">{run.environment_version}</div>
        </div>
        <div className="rounded-lg border border-border bg-bg-surface p-4">
          <div className="text-[10px] text-text-muted uppercase tracking-wider mb-1">Strategy</div>
          <div className="text-sm font-mono">
            {run.initial_strategy_version} → {run.final_strategy_version || '—'}
          </div>
        </div>
        <div className="rounded-lg border border-border bg-bg-surface p-4">
          <div className="text-[10px] text-text-muted uppercase tracking-wider mb-1">Duration</div>
          <div className="text-sm font-mono">
            {run.total_adaptation_ms ? (run.total_adaptation_ms / 1000).toFixed(2) + 's' : '—'}
          </div>
        </div>
      </div>

      {/* Failure banner */}
      {run.failure_reason && (
        <div className="mb-8 rounded-lg border border-status-warning/40 bg-status-warning/10 text-status-warning px-5 py-4">
          <div className="text-xs uppercase tracking-wider font-medium mb-1">Failure detected</div>
          <div className="text-sm">{run.failure_reason}</div>
        </div>
      )}

      {/* Strategy Diff */}
      <div className="mb-8">
        <h2 className="text-lg font-semibold mb-3">Strategy Diff</h2>
        <StrategyDiff before={before} after={after} />
      </div>

      {/* Diagnosis JSON */}
      {diagnosisStep?.data && (
        <div className="mb-8">
          <h2 className="text-lg font-semibold mb-3">Diagnosis</h2>
          <pre className="text-xs font-mono bg-bg-base rounded-lg p-4 border border-border overflow-x-auto">
{JSON.stringify(diagnosisStep.data, null, 2)}
          </pre>
        </div>
      )}

      {/* Validation */}
      {validationStep?.data && (
        <div className="mb-8">
          <h2 className="text-lg font-semibold mb-3">Validation</h2>
          <div className="rounded-lg border border-status-success/30 bg-status-success/5 p-4">
            <div className="flex items-center justify-between">
              <div className="text-sm">{validationStep.data.reason}</div>
              <div className="text-xs text-status-success font-mono">
                confidence: {(validationStep.data.confidence * 100).toFixed(0)}%
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Timeline */}
      <div className="mb-8">
        <h2 className="text-lg font-semibold mb-3">Adaptation Timeline</h2>
        <div className="rounded-xl border border-border bg-bg-surface overflow-hidden">
          {run.steps.map((step, i) => (
            <div key={i} className="flex items-start gap-3 px-5 py-3 border-b border-border/60 last:border-0">
              <div className="pt-0.5">{STEP_STATUS_ICON[step.status] || STEP_STATUS_ICON.running}</div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs uppercase tracking-wider text-text-muted font-mono">
                    {step.stage}
                  </span>
                  {step.duration_ms != null && (
                    <span className="text-[10px] text-text-muted font-mono">
                      +{step.duration_ms}ms
                    </span>
                  )}
                </div>
                <div className="text-sm text-text-primary">{step.message}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Final result */}
      {run.result && (
        <div className="mb-8">
          <h2 className="text-lg font-semibold mb-3">Final Result</h2>
          <pre className="text-xs font-mono bg-bg-base rounded-lg p-4 border border-status-success/30 overflow-x-auto">
{JSON.stringify(run.result, null, 2)}
          </pre>
        </div>
      )}

      <div className="text-xs text-text-muted">
        Created: {formatTime(run.created_at)}
      </div>
    </div>
  )
}
