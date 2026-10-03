import { Activity, Layers, Shield, Cpu, Database, Zap } from 'lucide-react'

function Section({ icon: Icon, title, children }) {
  return (
    <div className="mb-8">
      <div className="flex items-center gap-2 mb-3">
        <Icon className="w-4 h-4 text-accent" />
        <h2 className="text-lg font-semibold">{title}</h2>
      </div>
      <div className="text-sm text-text-secondary leading-relaxed pl-6">{children}</div>
    </div>
  )
}

export default function Docs() {
  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-4xl mx-auto">
      <div className="mb-10">
        <div className="text-xs text-accent uppercase tracking-widest font-medium mb-2">
          Reference
        </div>
        <h1 className="text-3xl font-semibold tracking-tight">Documentation</h1>
        <p className="text-text-secondary mt-1">
          Architecture, agents, and safety model of ShiftForge.
        </p>
      </div>

      <Section icon={Activity} title="Overview">
        ShiftForge is a self-adapting AI agent platform. When the external tools or APIs the agent
        depends on suddenly change — endpoint renamed, schema altered, fields moved — the agent
        detects the failure, diagnoses the change, generates a new strategy, tests it safely,
        and recovers — <span className="text-text-primary font-medium">all without human intervention.</span>
      </Section>

      <Section icon={Layers} title="Agent Architecture">
        Six specialized agents run in sequence, each producing structured JSON output:
        <ul className="list-disc list-inside mt-3 space-y-1.5">
          <li><span className="text-text-primary font-medium">Monitor</span> — detects contract mismatch</li>
          <li><span className="text-text-primary font-medium">Diagnosis</span> — compares old vs new contract</li>
          <li><span className="text-text-primary font-medium">Strategy</span> — generates replacement approach</li>
          <li><span className="text-text-primary font-medium">Sandbox</span> — tests strategy in isolation</li>
          <li><span className="text-text-primary font-medium">Validation</span> — confirms safety and correctness</li>
          <li><span className="text-text-primary font-medium">Recovery</span> — adopts strategy, retries original task</li>
        </ul>
      </Section>

      <Section icon={Shield} title="Safety Model">
        The LLM never executes code directly. It only reasons and produces structured JSON.
        The backend controls tool availability, environment state, and strategy acceptance.
        Every generated strategy must pass through the sandbox and validator before adoption.
        Unknown tools are rejected. Failed validation blocks recovery.
      </Section>

      <Section icon={Cpu} title="LLM Provider">
        Reasoning is handled by Groq's <code className="text-accent font-mono">gpt-oss-120b</code> model
        via structured JSON mode. Each agent uses a narrow, well-scoped prompt.
        No autonomous code execution. No uncontrolled external requests.
      </Section>

      <Section icon={Database} title="Persistence">
        All runs, adaptations, strategies, and environment versions are stored in SQLite.
        Every run has a unique ID (<code className="text-accent font-mono">SF-XXXXXX</code>),
        a full timeline of steps, and a complete recovery trace.
      </Section>

      <Section icon={Zap} title="Live Streaming">
        Every stage emits an SSE event at <code className="text-accent font-mono">/api/stream/{'{run_id}'}</code>.
        The frontend subscribes in real time and animates the workflow diagram as the pipeline runs.
      </Section>

      <div className="mt-12 pt-8 border-t border-border text-xs text-text-muted">
        ShiftForge · Self-Adapting AI Infrastructure · Built for resilience
      </div>
    </div>
  )
}
