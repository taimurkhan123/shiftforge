import { useEffect, useState } from 'react'
import { Activity, Server, GitBranch, RefreshCw, Clock, ArrowRight } from 'lucide-react'
import { Link } from 'react-router-dom'
import { getEnvironment, listAdaptations, listRuns } from '../lib/api'

function StatCard({ icon: Icon, label, value, sublabel, accent }) {
  return (
    <div className="rounded-xl border border-border bg-bg-surface p-5 hover:border-border/80 transition-colors">
      <div className="flex items-start justify-between">
        <div>
          <div className="text-xs text-text-muted uppercase tracking-wider">{label}</div>
          <div className="text-2xl font-semibold mt-2 font-mono">{value}</div>
          {sublabel && <div className="text-xs text-text-secondary mt-1">{sublabel}</div>}
        </div>
        <div className={'w-10 h-10 rounded-lg flex items-center justify-center ' + (accent || 'bg-accent/10 text-accent')}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
    </div>
  )
}

export default function Overview() {
  const [env, setEnv] = useState(null)
  const [adaptations, setAdaptations] = useState([])
  const [runs, setRuns] = useState([])

  useEffect(() => {
    const load = async () => {
      try {
        const [e, a, r] = await Promise.all([
          getEnvironment(),
          listAdaptations(),
          listRuns(),
        ])
        setEnv(e)
        setAdaptations(a.adaptations || [])
        setRuns(r.runs || [])
      } catch (err) {
        console.error(err)
      }
    }
    load()
  }, [])

  const lastRun = runs[0]
  const lastAdaptation = adaptations[0]
  const status = env ? 'Operational' : 'Connecting...'

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto">
      <div className="mb-10">
        <div className="text-xs text-accent uppercase tracking-widest font-medium mb-3">
          Self-Adapting AI Infrastructure
        </div>
        <h1 className="text-3xl sm:text-4xl font-semibold tracking-tight leading-tight max-w-3xl">
          Your Agent Shouldn&apos;t Stop<br />
          <span className="text-text-secondary">When Its Environment Changes.</span>
        </h1>
        <p className="text-text-secondary mt-4 max-w-2xl">
          ShiftForge detects environmental changes, builds a new strategy, tests it safely,
          and helps the agent continue working — no human intervention required.
        </p>
        <div className="flex gap-3 mt-6">
          <Link to="/demo" className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-accent hover:bg-accent-hover text-white font-medium transition-colors">
            Run Adaptation Demo
            <ArrowRight className="w-4 h-4" />
          </Link>
          <Link to="/agent-lab" className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg border border-border hover:bg-bg-elevated transition-colors">
            Explore Agent
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-10">
        <StatCard
          icon={Activity}
          label="Agent Status"
          value={status}
          sublabel={env ? 'Last check: just now' : 'Waiting for backend'}
          accent="bg-status-success/10 text-status-success"
        />
        <StatCard
          icon={Server}
          label="Environment"
          value={env ? env.active_version : '—'}
          sublabel={env ? env.contract.endpoint : ''}
        />
        <StatCard
          icon={GitBranch}
          label="Adaptations"
          value={adaptations.length}
          sublabel={lastAdaptation ? lastAdaptation.to_strategy : 'No adaptations yet'}
        />
        <StatCard
          icon={Clock}
          label="Last Recovery"
          value={lastRun && lastRun.total_adaptation_ms ? (lastRun.total_adaptation_ms / 1000).toFixed(1) + 's' : '—'}
          sublabel={lastRun ? lastRun.status : 'No runs yet'}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="rounded-xl border border-border bg-bg-surface p-6">
          <div className="flex items-center justify-between mb-5">
            <h2 className="font-semibold">Current Strategy</h2>
            <Link to="/environment" className="text-xs text-accent hover:text-accent-hover">
              Manage →
            </Link>
          </div>
          {env ? (
            <pre className="text-xs font-mono text-text-secondary bg-bg-base rounded-lg p-4 border border-border overflow-x-auto">
{JSON.stringify(env.contract, null, 2)}
            </pre>
          ) : (
            <div className="text-text-muted text-sm">Loading...</div>
          )}
        </div>

        <div className="rounded-xl border border-border bg-bg-surface p-6">
          <div className="flex items-center justify-between mb-5">
            <h2 className="font-semibold">Recent Adaptations</h2>
            <Link to="/adaptations" className="text-xs text-accent hover:text-accent-hover">
              View all →
            </Link>
          </div>
          {adaptations.length === 0 ? (
            <div className="text-text-muted text-sm py-8 text-center">
              No adaptations yet. Run the demo to see one.
            </div>
          ) : (
            <div className="space-y-2">
              {adaptations.slice(0, 3).map(a => (
                <div key={a.adaptation_id} className="flex items-center justify-between py-2 border-b border-border/50 last:border-0">
                  <div className="flex items-center gap-3">
                    <RefreshCw className="w-4 h-4 text-status-success" />
                    <div>
                      <div className="text-sm font-mono">{a.from_strategy} → {a.to_strategy}</div>
                      <div className="text-xs text-text-muted">{a.change_type}</div>
                    </div>
                  </div>
                  <div className="text-xs text-status-success">SUCCESS</div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
