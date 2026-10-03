import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import AppShell from './layouts/AppShell'
import Overview from './pages/Overview'
import DemoMode from './pages/DemoMode'
import AgentLab from './pages/AgentLab'
import Environment from './pages/Environment'
import Adaptations from './pages/Adaptations'
import Runs from './pages/Runs'
import RunDetail from './pages/RunDetail'
import Docs from './pages/Docs'
import Landing from './pages/Landing'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route element={<AppShell />}>
          <Route path="/dashboard" element={<Overview />} />
          <Route path="/demo" element={<DemoMode />} />
          <Route path="/agent-lab" element={<AgentLab />} />
          <Route path="/environment" element={<Environment />} />
          <Route path="/adaptations" element={<Adaptations />} />
          <Route path="/runs" element={<Runs />} />
          <Route path="/runs/:runId" element={<RunDetail />} />
          <Route path="/docs" element={<Docs />} />
        </Route>
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
