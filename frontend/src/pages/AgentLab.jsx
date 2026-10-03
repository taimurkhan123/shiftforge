import { useMemo, useState } from 'react'
import ReactFlow, { Background, Controls, MarkerType } from 'reactflow'
import 'reactflow/dist/style.css'
import {
  Radio, Search, GitBranch, Box, CheckCircle2, RefreshCw, Zap, ArrowRight,
  Cpu, Shield, Database, Activity
} from 'lucide-react'

const AGENTS = [
  {
    id: 'monitor',
    name: 'Monitor Agent',
    icon: Radio,
    color: '#3b82f6',
    role: 'Watches tool responses against the known contract.',
    input: 'Tool response + expected contract',
    output: '{ status, severity, reason }',
    highlight: 'Detects the change',
  },
  {
    id: 'diagnosis',
    name: 'Diagnosis Agent',
    icon: Search,
    color: '#8b5cf6',
    role: 'Compares old contract to new contract.',
    input: 'Old contract + new contract',
    output: '{ removed, added, endpoints }',
    highlight: 'Understands the change',
  },
  {
    id: 'strategy',
    name: 'Strategy Agent',
    icon: GitBranch,
    color: '#ec4899',
    role: 'Produces a new strategy for the new contract.',
    input: 'Diagnosis + new contract',
    output: '{ endpoint, fields, version }',
    highlight: 'Builds the fix',
  },
  {
    id: 'sandbox',
    name: 'Sandbox Agent',
    icon: Box,
    color: '#f59e0b',
    role: 'Tests the strategy against a simulated environment.',
    input: 'Strategy + target contract',
    output: '{ passed, output, error }',
    highlight: 'Tests safely',
  },
  {
    id: 'validation',
    name: 'Validation Agent',
    icon: CheckCircle2,
    color: '#10b981',
    role: 'Confirms the strategy is correct and safe.',
    input: 'Sandbox result + original task',
    output: '{ validated, confidence, reason }',
    highlight: 'Gates adoption',
  },
  {
    id: 'recovery',
    name: 'Recovery Agent',
    icon: RefreshCw,
    color: '#6366f1',
    role: 'Adopts the strategy and retries the original task.',
    input: 'Validated strategy',
    output: 'Final task result',
    highlight: 'Restores service',
  },
]

function HubNode({ data }) {
  const Icon = data.icon
  return (
    <div
      className="rounded-xl border-2 px-4 py-3 flex flex-col items-center justify-center transition-all duration-300"
      style={{
        width: 160,
        height: 100,
        borderColor: data.color,
        background: '#12121a',
        boxShadow: data.selected ? '0 0 32px -8px ' + data.color + '99' : 'none',
      }}
    >
      <div
        className="w-8 h-8 rounded-lg flex items-center justify-center mb-2"
        style={{ background: data.color + '20', color: data.color }}
      >
        <Icon className="w-4 h-4" />
      </div>
      <div className="text-xs font-medium text-center leading-tight">{data.label}</div>
      <div className="text-[9px] uppercase tracking-wider mt-1" style={{ color: data.color }}>
        Agent
      </div>
    </div>
  )
}

function CenterNode() {
  return (
    <div className="rounded-2xl border-2 border-accent bg-bg-elevated px-6 py-5 flex flex-col items-center justify-center"
         style={{ width: 200, height: 130, boxShadow: '0 0 60px -10px rgba(99,102,241,0.7)' }}>
      <div className="w-12 h-12 rounded-xl bg-accent/20 border border-accent/40 flex items-center justify-center mb-2">
        <Zap className="w-6 h-6 text-accent" />
      </div>
      <div className="text-sm font-semibold">ShiftForge</div>
      <div className="text-[10px] text-text-muted uppercase tracking-wider mt-1">
        Adaptation Engine
      </div>
    </div>
  )
}

function AgentCard({ agent, selected, onSelect }) {
  const Icon = agent.icon
  return (
    <button
      onClick={onSelect}
      className={
        'text-left rounded-xl border bg-bg-surface p-4 transition-all w-full ' +
        (selected ? 'border-accent/60 bg-accent/5' : 'border-border hover:border-border/80 hover:bg-bg-elevated')
      }
    >
      <div className="flex items-start gap-3">
        <div
          className="w-9 h-9 rounded-lg flex items-center justify-center shrink-0"
          style={{ background: agent.color + '20', color: agent.color }}
        >
          <Icon className="w-4 h-4" />
        </div>
        <div className="min-w-0">
          <div className="text-sm font-medium">{agent.name}</div>
          <div className="text-xs text-text-muted mt-0.5 line-clamp-2">{agent.role}</div>
        </div>
      </div>
    </button>
  )
}

function useGraphData() {
  return useMemo(() => {
    const centerX = 500
    const centerY = 500
    const radius = 320

    const nodes = [
      {
        id: 'hub',
        type: 'center',
        position: { x: centerX - 100, y: centerY - 65 },
        data: {},
        draggable: false,
      },
    ]

    const edges = []

    AGENTS.forEach((agent, i) => {
      const angle = (i / AGENTS.length) * Math.PI * 2 - Math.PI / 2
      const x = centerX + Math.cos(angle) * radius - 80
      const y = centerY + Math.sin(angle) * radius - 50

      nodes.push({
        id: agent.id,
        type: 'hub',
        position: { x, y },
        data: { label: agent.name.replace(' Agent', ''), icon: agent.icon, color: agent.color },
        draggable: false,
      })

      edges.push({
        id: 'hub-' + agent.id,
        source: 'hub',
        target: agent.id,
        type: 'straight',
        style: { stroke: agent.color + '60', strokeWidth: 1.5, strokeDasharray: '4 4' },
        markerEnd: { type: MarkerType.ArrowClosed, color: agent.color + '60' },
      })

      // Link each agent to the next in the pipeline (dotted outer ring)
      const next = AGENTS[(i + 1) % AGENTS.length]
      edges.push({
        id: 'pipeline-' + agent.id,
        source: agent.id,
        target: next.id,
        type: 'default',
        style: { stroke: agent.color + '30', strokeWidth: 1 },
      })
    })

    return { nodes, edges }
  }, [])
}

export default function AgentLab() {
  const { nodes, edges } = useGraphData()
  const [selected, setSelected] = useState(null)

  const nodeTypes = useMemo(() => ({ center: CenterNode, hub: HubNode }), [])

  const agent = AGENTS.find(a => a.id === selected)

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto">
      <div className="mb-8">
        <div className="text-xs text-accent uppercase tracking-widest font-medium mb-2">
          Architecture
        </div>
        <h1 className="text-3xl font-semibold tracking-tight">Agent Lab</h1>
        <p className="text-text-secondary mt-1">
          Six specialized agents orchestrate the adaptation. Each produces structured JSON output.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="lg:col-span-2 rounded-xl border border-border bg-bg-surface p-4">
          <div className="text-xs text-text-muted uppercase tracking-wider mb-2 px-1">
            Orchestration Graph
          </div>
          <div style={{ width: '100%', height: 660 }}>
            <ReactFlow
              nodes={nodes}
              edges={edges}
              nodeTypes={nodeTypes}
              fitView
              fitViewOptions={{ padding: 0.15 }}
              proOptions={{ hideAttribution: true }}
              nodesDraggable={false}
              nodesConnectable={false}
              elementsSelectable={true}
            >
              <Background color="#1a1a24" gap={24} />
              <Controls showInteractive={false} />
            </ReactFlow>
          </div>
        </div>

        <div className="space-y-3">
          <div className="text-xs text-text-muted uppercase tracking-wider px-1">
            Agents ({AGENTS.length})
          </div>
          {AGENTS.map(a => (
            <AgentCard
              key={a.id}
              agent={a}
              selected={selected === a.id}
              onSelect={() => setSelected(selected === a.id ? null : a.id)}
            />
          ))}
        </div>
      </div>

      {agent && (
        <div className="rounded-xl border border-border bg-bg-surface p-6 mb-8">
          <div className="flex items-start gap-4 mb-6">
            <div
              className="w-12 h-12 rounded-xl flex items-center justify-center shrink-0"
              style={{ background: agent.color + '20', color: agent.color }}
            >
              <agent.icon className="w-6 h-6" />
            </div>
            <div>
              <div className="text-xs uppercase tracking-wider mb-1" style={{ color: agent.color }}>
                {agent.highlight}
              </div>
              <h2 className="text-xl font-semibold">{agent.name}</h2>
              <p className="text-sm text-text-secondary mt-1">{agent.role}</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="rounded-lg border border-border bg-bg-base p-4">
              <div className="text-[10px] text-text-muted uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <ArrowRight className="w-3 h-3" /> Input
              </div>
              <div className="text-sm font-mono text-text-primary">{agent.input}</div>
            </div>
            <div className="rounded-lg border border-border bg-bg-base p-4">
              <div className="text-[10px] text-text-muted uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <ArrowRight className="w-3 h-3" /> Output
              </div>
              <div className="text-sm font-mono text-text-primary">{agent.output}</div>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="rounded-xl border border-border bg-bg-surface p-5">
          <div className="flex items-center gap-2 mb-3">
            <Cpu className="w-4 h-4 text-accent" />
            <h3 className="text-sm font-semibold">LLM Provider</h3>
          </div>
          <div className="text-xs text-text-secondary">
            Groq · <span className="font-mono text-accent">gpt-oss-120b</span>
          </div>
          <div className="text-[10px] text-text-muted mt-2">
            Structured JSON mode · no code execution
          </div>
        </div>

        <div className="rounded-xl border border-border bg-bg-surface p-5">
          <div className="flex items-center gap-2 mb-3">
            <Shield className="w-4 h-4 text-status-success" />
            <h3 className="text-sm font-semibold">Safety Model</h3>
          </div>
          <div className="text-xs text-text-secondary">
            Predefined tools only. Sandbox before adoption. Validation gate.
          </div>
          <div className="text-[10px] text-text-muted mt-2">
            No arbitrary code · no dynamic imports
          </div>
        </div>

        <div className="rounded-xl border border-border bg-bg-surface p-5">
          <div className="flex items-center gap-2 mb-3">
            <Activity className="w-4 h-4 text-status-info" />
            <h3 className="text-sm font-semibold">Live Streaming</h3>
          </div>
          <div className="text-xs text-text-secondary">
            SSE events at <span className="font-mono text-accent">/api/stream/{'{run_id}'}</span>
          </div>
          <div className="text-[10px] text-text-muted mt-2">
            Real-time workflow animation
          </div>
        </div>
      </div>
    </div>
  )
}
