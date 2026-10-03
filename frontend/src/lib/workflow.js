export const WORKFLOW_STAGES = [
  { id: 'monitor',      label: 'Monitor',        desc: 'Watching tool responses' },
  { id: 'change',       label: 'Change Detected',desc: 'Contract mismatch found' },
  { id: 'diagnosis',    label: 'Diagnoser',      desc: 'Comparing old vs new' },
  { id: 'strategy',     label: 'Strategy Builder',desc: 'Generating new plan' },
  { id: 'sandbox',      label: 'Sandbox',        desc: 'Testing safely' },
  { id: 'validation',   label: 'Validator',      desc: 'Checking confidence' },
  { id: 'recovery',     label: 'Recovery',       desc: 'Adopting & retrying' },
  { id: 'complete',     label: 'Task Completed', desc: 'Original goal achieved' },
]

// Map backend stage names -> workflow node id
export const STAGE_TO_NODE = {
  monitor: 'monitor',
  change_detected: 'change',
  diagnosis: 'diagnosis',
  strategy: 'strategy',
  sandbox: 'sandbox',
  validation: 'validation',
  recovery: 'recovery',
  complete: 'complete',
}

export function initialNodeStatus() {
  const s = {}
  WORKFLOW_STAGES.forEach(n => s[n.id] = 'idle')
  return s
}
