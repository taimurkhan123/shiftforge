import { Handle, Position } from 'reactflow'
import { Radio, AlertTriangle, Search, GitBranch, Box, CheckCircle2, RefreshCw, Flag } from 'lucide-react'

const ICONS = {
  monitor: Radio,
  change: AlertTriangle,
  diagnosis: Search,
  strategy: GitBranch,
  sandbox: Box,
  validation: CheckCircle2,
  recovery: RefreshCw,
  complete: Flag,
}

const STATUS_STYLES = {
  idle:    { border: '#2a2a36',         bg: '#12121a', icon: 'text-text-muted',    dot: 'bg-text-muted' },
  running: { border: '#6366f1',         bg: '#1a1a2e', icon: 'text-accent',        dot: 'bg-accent animate-pulse', glow: '0 0 24px -6px rgba(99,102,241,0.6)' },
  success: { border: '#10b981',         bg: '#0f1f1a', icon: 'text-status-success', dot: 'bg-status-success' },
  warning: { border: '#f59e0b',         bg: '#1f180a', icon: 'text-status-warning', dot: 'bg-status-warning' },
  failed:  { border: '#ef4444',         bg: '#1f0f0f', icon: 'text-status-danger',  dot: 'bg-status-danger' },
}

export default function WorkflowNode({ data }) {
  const Icon = ICONS[data.label.toLowerCase().split(' ')[0]] || ICONS[data.label] || Radio
  const s = STATUS_STYLES[data.status] || STATUS_STYLES.idle

  return (
    <div
      style={{
        width: 200,
        height: 92,
        borderColor: s.border,
        background: s.bg,
        boxShadow: s.glow || 'none',
      }}
      className="rounded-xl border-2 px-4 py-3 flex flex-col justify-between transition-all duration-300"
    >
      <Handle type="target" position={Position.Top} style={{ opacity: 0 }} />
      <div className="flex items-center gap-2">
        <div className={'w-6 h-6 rounded-md flex items-center justify-center bg-black/30 ' + s.icon}>
          <Icon className="w-3.5 h-3.5" />
        </div>
        <div className="text-sm font-medium text-text-primary truncate">{data.label}</div>
      </div>
      <div className="text-[11px] text-text-muted truncate">{data.desc}</div>
      <div className="flex items-center gap-1.5 mt-1">
        <span className={'w-1.5 h-1.5 rounded-full ' + s.dot} />
        <span className="text-[10px] uppercase tracking-wider text-text-secondary">
          {data.status}
        </span>
      </div>
      <Handle type="source" position={Position.Bottom} style={{ opacity: 0 }} />
    </div>
  )
}
