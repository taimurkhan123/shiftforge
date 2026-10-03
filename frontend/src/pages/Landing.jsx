import { Link } from 'react-router-dom'
import {
  Activity, ArrowRight, Zap, Shield, GitBranch, Box, CheckCircle2,
  RefreshCw, Search, Radio, Cpu, TrendingUp, Users, Clock, AlertTriangle
} from 'lucide-react'

function Hero() {
  return (
    <section className="px-6 py-24 md:py-32 max-w-6xl mx-auto text-center">
      <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-accent/10 border border-accent/30 text-accent text-xs mb-8">
        <Activity className="w-3.5 h-3.5" />
        Self-Adapting AI Infrastructure
      </div>
      <h1 className="text-5xl md:text-6xl font-semibold tracking-tight leading-[1.05] mb-6">
        AI Agents Should Adapt.<br />
        <span className="text-text-muted">Not Collapse.</span>
      </h1>
      <p className="text-text-secondary text-lg md:text-xl mb-10 max-w-2xl mx-auto">
        ShiftForge gives autonomous agents the ability to detect environmental changes,
        test new strategies, and recover safely — automatically.
      </p>
      <div className="flex flex-col sm:flex-row gap-3 justify-center">
        <Link to="/demo" className="inline-flex items-center justify-center gap-2 px-6 py-3 rounded-lg bg-accent hover:bg-accent-hover text-white font-medium transition-colors">
          Run Live Demo <ArrowRight className="w-4 h-4" />
        </Link>
        <Link to="/agent-lab" className="inline-flex items-center justify-center gap-2 px-6 py-3 rounded-lg border border-border hover:bg-bg-elevated transition-colors">
          Explore Architecture
        </Link>
      </div>
    </section>
  )
}

function Problem() {
  return (
    <section className="px-6 py-20 border-t border-border bg-bg-surface/30">
      <div className="max-w-5xl mx-auto">
        <div className="text-xs text-accent uppercase tracking-widest font-medium mb-3 text-center">The Problem</div>
        <h2 className="text-3xl md:text-4xl font-semibold tracking-tight text-center mb-14">
          Agents break when their world changes.
        </h2>
        <div className="grid md:grid-cols-3 gap-6">
          <div className="rounded-xl border border-border bg-bg-surface p-6">
            <AlertTriangle className="w-6 h-6 text-status-warning mb-4" />
            <h3 className="font-medium mb-2">APIs change constantly</h3>
            <p className="text-sm text-text-secondary">Endpoints get renamed. Fields move. Schemas evolve. Every week, somewhere.</p>
          </div>
          <div className="rounded-xl border border-border bg-bg-surface p-6">
            <AlertTriangle className="w-6 h-6 text-status-danger mb-4" />
            <h3 className="font-medium mb-2">Agents fail silently or loudly</h3>
            <p className="text-sm text-text-secondary">When the tool contract breaks, the agent either crashes or returns garbage.</p>
          </div>
          <div className="rounded-xl border border-border bg-bg-surface p-6">
            <Users className="w-6 h-6 text-accent mb-4" />
            <h3 className="font-medium mb-2">A human gets paged at 2am</h3>
            <p className="text-sm text-text-secondary">Somebody has to find what changed, fix the code, test it, and redeploy.</p>
          </div>
        </div>
      </div>
    </section>
  )
}

function HowItWorks() {
  const steps = [
    { icon: Radio, label: 'Detect', desc: 'Monitor notices the mismatch' },
    { icon: Search, label: 'Diagnose', desc: 'Diagnosis identifies the change' },
    { icon: GitBranch, label: 'Strategize', desc: 'Strategy builds a replacement' },
    { icon: Box, label: 'Test', desc: 'Sandbox runs it safely' },
    { icon: CheckCircle2, label: 'Validate', desc: 'Validation confirms safety' },
    { icon: RefreshCw, label: 'Recover', desc: 'Recovery adopts and retries' },
  ]
  return (
    <section className="px-6 py-20">
      <div className="max-w-6xl mx-auto">
        <div className="text-xs text-accent uppercase tracking-widest font-medium mb-3 text-center">How ShiftForge Works</div>
        <h2 className="text-3xl md:text-4xl font-semibold tracking-tight text-center mb-14">
          Six agents. One autonomous loop.
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {steps.map((s, i) => (
            <div key={s.label} className="text-center">
              <div className="w-12 h-12 rounded-xl bg-accent/10 border border-accent/30 flex items-center justify-center mx-auto mb-3">
                <s.icon className="w-5 h-5 text-accent" />
              </div>
              <div className="text-xs text-text-muted font-mono mb-1">STEP {i + 1}</div>
              <div className="font-medium mb-1">{s.label}</div>
              <div className="text-xs text-text-secondary">{s.desc}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

function LiveDemoSection() {
  return (
    <section className="px-6 py-20 border-t border-border bg-bg-surface/30">
      <div className="max-w-4xl mx-auto text-center">
        <div className="text-xs text-accent uppercase tracking-widest font-medium mb-3">Live Demonstration</div>
        <h2 className="text-3xl md:text-4xl font-semibold tracking-tight mb-6">
          Watch it adapt. In four seconds.
        </h2>
        <p className="text-text-secondary mb-10 max-w-2xl mx-auto">
          Break the environment, and watch ShiftForge detect the change, generate a new strategy, test it safely, and recover — all in real time.
        </p>
        <div className="inline-flex items-center gap-3 rounded-xl border border-border bg-bg-surface px-6 py-5 font-mono text-sm">
          <span className="w-2 h-2 rounded-full bg-status-success animate-pulse" />
          <span className="text-text-muted">/api/weather</span>
          <ArrowRight className="w-4 h-4 text-text-muted" />
          <span className="text-status-danger">/api/forecast</span>
          <ArrowRight className="w-4 h-4 text-text-muted" />
          <span className="text-status-success">auto-recovered</span>
        </div>
        <div className="mt-8">
          <Link to="/demo" className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-accent hover:bg-accent-hover text-white font-medium transition-colors">
            <Zap className="w-4 h-4" /> Start the Demo
          </Link>
        </div>
      </div>
    </section>
  )
}

function Architecture() {
  return (
    <section className="px-6 py-20">
      <div className="max-w-5xl mx-auto">
        <div className="text-xs text-accent uppercase tracking-widest font-medium mb-3 text-center">Agent Architecture</div>
        <h2 className="text-3xl md:text-4xl font-semibold tracking-tight text-center mb-14">
          CrewAI orchestration. Deterministic safety.
        </h2>
        <div className="grid md:grid-cols-2 gap-6">
          <div className="rounded-xl border border-border bg-bg-surface p-6">
            <Cpu className="w-5 h-5 text-accent mb-4" />
            <h3 className="font-medium mb-3">Reasoning Agents (CrewAI)</h3>
            <ul className="text-sm text-text-secondary space-y-2">
              <li>• Monitor — detects contract mismatch</li>
              <li>• Diagnosis — identifies what changed</li>
              <li>• Strategy — generates a replacement plan</li>
              <li>• Validation — approves before adoption</li>
            </ul>
          </div>
          <div className="rounded-xl border border-border bg-bg-surface p-6">
            <Shield className="w-5 h-5 text-status-success mb-4" />
            <h3 className="font-medium mb-3">Deterministic Steps (Safe)</h3>
            <ul className="text-sm text-text-secondary space-y-2">
              <li>• Sandbox — tests strategy in isolation</li>
              <li>• Recovery — adopts and retries task</li>
              <li>• Only registered tools can be called</li>
              <li>• No arbitrary code. Ever.</li>
            </ul>
          </div>
        </div>
      </div>
    </section>
  )
}

function WhyItMatters() {
  return (
    <section className="px-6 py-20 border-t border-border bg-bg-surface/30">
      <div className="max-w-5xl mx-auto">
        <div className="text-xs text-accent uppercase tracking-widest font-medium mb-3 text-center">Why It Matters</div>
        <h2 className="text-3xl md:text-4xl font-semibold tracking-tight text-center mb-14">
          The reliability layer for the agentic era.
        </h2>
        <div className="grid md:grid-cols-3 gap-6">
          <div className="rounded-xl border border-border bg-bg-surface p-6 text-center">
            <Clock className="w-6 h-6 text-accent mx-auto mb-3" />
            <div className="text-3xl font-semibold mb-2">4s</div>
            <div className="text-sm text-text-secondary">vs 2-6 hours for a human fix</div>
          </div>
          <div className="rounded-xl border border-border bg-bg-surface p-6 text-center">
            <TrendingUp className="w-6 h-6 text-status-success mx-auto mb-3" />
            <div className="text-3xl font-semibold mb-2">99.9%</div>
            <div className="text-sm text-text-secondary">agent uptime, no on-call pager</div>
          </div>
          <div className="rounded-xl border border-border bg-bg-surface p-6 text-center">
            <Users className="w-6 h-6 text-accent mx-auto mb-3" />
            <div className="text-3xl font-semibold mb-2">0</div>
            <div className="text-sm text-text-secondary">engineers woken up at 2am</div>
          </div>
        </div>
      </div>
    </section>
  )
}

function Technology() {
  const techs = [
    { name: 'CrewAI', role: 'Agent orchestration' },
    { name: 'Groq', role: 'LLM inference' },
    { name: 'FastAPI', role: 'Backend API' },
    { name: 'React Flow', role: 'Workflow visualization' },
    { name: 'Pydantic', role: 'Structured outputs' },
    { name: 'SQLModel', role: 'Persistence' },
    { name: 'SSE', role: 'Live streaming' },
    { name: 'Tailwind', role: 'Design system' },
  ]
  return (
    <section className="px-6 py-20">
      <div className="max-w-5xl mx-auto">
        <div className="text-xs text-accent uppercase tracking-widest font-medium mb-3 text-center">Technology</div>
        <h2 className="text-3xl md:text-4xl font-semibold tracking-tight text-center mb-14">
          Built with the modern agent stack.
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {techs.map(t => (
            <div key={t.name} className="rounded-lg border border-border bg-bg-surface p-4 text-center">
              <div className="font-medium mb-1">{t.name}</div>
              <div className="text-xs text-text-muted">{t.role}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

function CTA() {
  return (
    <section className="px-6 py-24 border-t border-border">
      <div className="max-w-3xl mx-auto text-center">
        <h2 className="text-4xl md:text-5xl font-semibold tracking-tight leading-tight mb-6">
          Make the agents you already have<br />
          <span className="text-accent">indestructible.</span>
        </h2>
        <p className="text-text-secondary text-lg mb-10">
          Traditional agents are designed for known environments.<br />
          ShiftForge is designed for environments that change.
        </p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Link to="/demo" className="inline-flex items-center justify-center gap-2 px-6 py-3 rounded-lg bg-accent hover:bg-accent-hover text-white font-medium transition-colors">
            Run Live Demo <ArrowRight className="w-4 h-4" />
          </Link>
          <Link to="/dashboard" className="inline-flex items-center justify-center gap-2 px-6 py-3 rounded-lg border border-border hover:bg-bg-elevated transition-colors">
            Open Dashboard
          </Link>
        </div>
      </div>
    </section>
  )
}

export default function Landing() {
  return (
    <div className="min-h-screen bg-bg-base">
      <Hero />
      <Problem />
      <HowItWorks />
      <LiveDemoSection />
      <Architecture />
      <WhyItMatters />
      <Technology />
      <CTA />
      <footer className="px-6 py-10 border-t border-border text-center text-xs text-text-muted">
        ShiftForge · Self-Adapting AI Infrastructure · When the environment changes, your agent adapts.
      </footer>
    </div>
  )
}
