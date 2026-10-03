import { useMemo } from 'react'
import ReactFlow, { Background, Controls, MarkerType } from 'reactflow'
import 'reactflow/dist/style.css'
import { WORKFLOW_STAGES } from '../lib/workflow'
import WorkflowNode from './WorkflowNode'

// Defined OUTSIDE the component so React Flow doesn't see a new object per render
const nodeTypes = { workflow: WorkflowNode }

const NODE_HEIGHT = 92
const VERTICAL_GAP = 40

export default function WorkflowDiagram({ statuses = {} }) {
  const { nodes, edges } = useMemo(() => {
    const ns = WORKFLOW_STAGES.map((stage, idx) => ({
      id: stage.id,
      type: 'workflow',
      position: { x: 0, y: idx * (NODE_HEIGHT + VERTICAL_GAP) },
      data: {
        label: stage.label,
        desc: stage.desc,
        status: statuses[stage.id] || 'idle',
      },
      draggable: false,
    }))

    const es = []
    for (let i = 0; i < WORKFLOW_STAGES.length - 1; i++) {
      es.push({
        id: 'e' + i,
        source: WORKFLOW_STAGES[i].id,
        target: WORKFLOW_STAGES[i + 1].id,
        type: 'smoothstep',
        animated: false,
        style: { stroke: '#2a2a36', strokeWidth: 2 },
        markerEnd: { type: MarkerType.ArrowClosed, color: '#2a2a36' },
      })
    }

    return { nodes: ns, edges: es }
  }, [statuses])

  return (
    <div style={{ width: '100%', height: 820 }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        proOptions={{ hideAttribution: true }}
        nodesDraggable={false}
        nodesConnectable={false}
        elementsSelectable={false}
      >
        <Background color="#1a1a24" gap={20} />
        <Controls showInteractive={false} />
      </ReactFlow>
    </div>
  )
}
