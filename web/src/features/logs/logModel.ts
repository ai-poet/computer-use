import type { RunLogState, TerminalLine } from './types';

export type LogFilterKey = 'all' | 'thinking' | 'tool' | 'todo' | 'result' | 'hook' | 'raw';

export const LOG_FILTERS: Array<{ key: LogFilterKey; label: string }> = [
  { key: 'all', label: '全部' },
  { key: 'thinking', label: 'Thinking' },
  { key: 'tool', label: '工具' },
  { key: 'todo', label: 'Todo' },
  { key: 'result', label: '结果' },
  { key: 'hook', label: 'Hook' },
  { key: 'raw', label: 'Raw' }
];

export function lineMatches(line: TerminalLine, filter: LogFilterKey): boolean {
  if (filter === 'all') return true;
  if (filter === 'tool') return line.kind === 'tool_use' || line.kind === 'tool_result';
  return line.kind === filter;
}

export function todoGlyph(status?: string): string {
  if (status === 'completed') return '☑';
  if (status === 'in_progress') return '◐';
  if (status === 'pending') return '☐';
  return '·';
}

export function displayText(line: TerminalLine): string {
  if (line.kind === 'tool_use' && line.tool) {
    const summary = typeof line.meta?.summary === 'string' ? line.meta.summary : '';
    return `● ${line.tool}${summary ? ` ${summary}` : ''}`;
  }
  return line.text;
}

export function logTextForExport(log: Pick<RunLogState, 'rawLog' | 'lines'>): string {
  return log.rawLog || log.lines.map(displayText).join('\n');
}
