import { NavLink, Outlet, useLocation } from 'react-router-dom'
import { Activity, LayoutDashboard, FlaskConical, Server, History, ListChecks, BookOpen, PlayCircle, Menu, X } from 'lucide-react'
import { useEffect, useState } from 'react'
import { getHealth } from '../lib/api'

const NAV = [
  { to: '/dashboard',   label: 'Overview',      icon: LayoutDashboard },
  { to: '/demo',        label: 'Demo Mode',     icon: PlayCircle, highlight: true },
  { to: '/agent-lab',   label: 'Agent Lab',     icon: FlaskConical },
  { to: '/environment', label: 'Environment',   icon: Server },
  { to: '/adaptations', label: 'Adaptations',   icon: History },
  { to: '/runs',        label: 'Runs',          icon: ListChecks },
  { to: '/docs',        label: 'Documentation', icon: BookOpen },
]

export default function AppShell() {
  const [envVersion, setEnvVersion] = useState('...')
  const [online, setOnline] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const location = useLocation()

  useEffect(() => {
    setSidebarOpen(false)
  }, [location.pathname])

  useEffect(() => {
    let cancelled = false
    const poll = async () => {
      try {
        const h = await getHealth()
        if (!cancelled) {
          setEnvVersion(h.environment_version)
          setOnline(true)
        }
      } catch {
        if (!cancelled) setOnline(false)
      }
    }
    poll()
    const t = setInterval(poll, 5000)
    return () => { cancelled = true; clearInterval(t) }
  }, [])

  const SidebarContent = (
    <>
      <div className="h-16 px-5 flex items-center border-b border-border justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-accent/10 border border-accent/30 flex items-center justify-center">
            <Activity className="w-4 h-4 text-accent" />
          </div>
          <div>
            <div className="font-semibold tracking-tight leading-none">
              Shift<span className="text-accent">Forge</span>
            </div>
            <div className="text-[10px] text-text-muted mt-0.5">Self-Adapting AI</div>
          </div>
        </div>
        <button
          onClick={() => setSidebarOpen(false)}
          className="lg:hidden p-1 text-text-muted hover:text-text-primary"
          aria-label="Close sidebar"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      <nav className="flex-1 p-3 space-y-0.5 overflow-y-auto">
        {NAV.map(item => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              'flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ' +
              (isActive
                ? 'bg-accent/10 text-accent border border-accent/20'
                : 'text-text-secondary hover:text-text-primary hover:bg-bg-elevated border border-transparent')
            }
          >
            <item.icon className="w-4 h-4" />
            <span>{item.label}</span>
            {item.highlight && (
              <span className="ml-auto text-[10px] px-1.5 py-0.5 rounded bg-accent/20 text-accent">
                LIVE
              </span>
            )}
          </NavLink>
        ))}
      </nav>

      <div className="p-3 border-t border-border">
        <div className="flex items-center justify-between text-xs">
          <div className="flex items-center gap-2 text-text-secondary">
            <span className={'w-2 h-2 rounded-full ' + (online ? 'bg-status-success animate-pulse' : 'bg-status-danger')} />
            {online ? 'Backend online' : 'Backend offline'}
          </div>
          <span className="text-text-muted font-mono">{envVersion}</span>
        </div>
      </div>
    </>
  )

  return (
    <div className="min-h-screen flex bg-bg-base">
      <aside className="hidden lg:flex w-64 shrink-0 border-r border-border bg-bg-surface flex-col">
        {SidebarContent}
      </aside>

      {sidebarOpen && (
        <>
          <div
            className="lg:hidden fixed inset-0 bg-black/60 z-40"
            onClick={() => setSidebarOpen(false)}
          />
          <aside className="lg:hidden fixed inset-y-0 left-0 w-64 z-50 border-r border-border bg-bg-surface flex flex-col">
            {SidebarContent}
          </aside>
        </>
      )}

      <main className="flex-1 min-w-0 overflow-y-auto flex flex-col">
        <div className="lg:hidden sticky top-0 z-30 h-14 border-b border-border bg-bg-surface/95 backdrop-blur flex items-center px-4 gap-3">
          <button
            onClick={() => setSidebarOpen(true)}
            className="p-2 -ml-2 text-text-secondary hover:text-text-primary"
            aria-label="Open sidebar"
          >
            <Menu className="w-5 h-5" />
          </button>
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-accent/10 border border-accent/30 flex items-center justify-center">
              <Activity className="w-3.5 h-3.5 text-accent" />
            </div>
            <span className="font-semibold tracking-tight">
              Shift<span className="text-accent">Forge</span>
            </span>
          </div>
          <div className="ml-auto flex items-center gap-2 text-xs">
            <span className={'w-2 h-2 rounded-full ' + (online ? 'bg-status-success animate-pulse' : 'bg-status-danger')} />
            <span className="text-text-muted font-mono">{envVersion}</span>
          </div>
        </div>

        <Outlet />
      </main>
    </div>
  )
}
