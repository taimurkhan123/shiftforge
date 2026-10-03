import { DiffEditor } from '@monaco-editor/react'

export default function StrategyDiff({ before, after }) {
  const beforeText = [
    'GET ' + (before?.endpoint || '/api/weather'),
    'response.' + (before?.temperature_field || 'temperature'),
    'response.' + (before?.condition_field || 'condition'),
  ].join('\n')

  const afterText = [
    'GET ' + (after?.endpoint || '/api/forecast'),
    'response.' + (after?.temperature_field || 'temp_c'),
    'response.' + (after?.condition_field || 'weather'),
  ].join('\n')

  return (
    <div className="rounded-xl border border-border bg-bg-base overflow-hidden">
      <div className="px-4 py-2.5 border-b border-border flex items-center justify-between">
        <div className="text-xs text-text-muted font-mono">strategy.diff</div>
        <div className="flex gap-3 text-[10px] uppercase tracking-wider">
          <span className="text-status-danger">- before</span>
          <span className="text-status-success">+ after</span>
        </div>
      </div>
      <DiffEditor
        key={beforeText + '|' + afterText}
        height="260px"
        original={beforeText}
        modified={afterText}
        language="plaintext"
        theme="vs-dark"
        keepCurrentOriginalModel={true}
        keepCurrentModifiedModel={true}
        options={{
          readOnly: true,
          renderSideBySide: true,
          minimap: { enabled: false },
          scrollBeyondLastLine: false,
          fontSize: 13,
          fontFamily: 'JetBrains Mono, Consolas, monospace',
          lineNumbers: 'off',
          renderOverviewRuler: false,
          scrollbar: { vertical: 'hidden', horizontal: 'hidden' },
          padding: { top: 14, bottom: 14 },
          hideUnchangedRegions: { enabled: false },
          useInlineViewWhenSpaceIsLimited: true,
          renderIndicators: true,
        }}
      />
    </div>
  )
}
