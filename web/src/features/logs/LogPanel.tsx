import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Check, Copy, Download, Terminal } from 'lucide-react';
import { Button } from '../../shared/ui/Button';
import { EmptyState } from '../../shared/ui/EmptyState';
import { cn } from '../../shared/lib/cn';
import type { Run } from '../runs/types';
import type { RunLogState, TerminalLine } from './types';
import styles from './LogPanel.module.less';

type FilterKey = 'all' | 'thinking' | 'tool' | 'todo' | 'result' | 'hook' | 'raw';

const filters: Array<{ key: FilterKey; label: string }> = [
  { key: 'all', label: '全部' },
  { key: 'thinking', label: 'Thinking' },
  { key: 'tool', label: '工具' },
  { key: 'todo', label: 'Todo' },
  { key: 'result', label: '结果' },
  { key: 'hook', label: 'Hook' },
  { key: 'raw', label: 'Raw' }
];

function lineMatches(line: TerminalLine, filter: FilterKey) {
  if (filter === 'all') return true;
  if (filter === 'tool') return line.kind === 'tool_use' || line.kind === 'tool_result';
  return line.kind === filter;
}

function todoGlyph(status?: string) {
  if (status === 'completed') return '☑';
  if (status === 'in_progress') return '◐';
  if (status === 'pending') return '☐';
  return '·';
}

function lineClass(line: TerminalLine) {
  return cn(
    styles.line,
    line.indent === 1 && styles.indent1,
    line.indent === 2 && styles.indent2,
    line.kind === 'thinking' && styles.thinking,
    line.tone === 'muted' && styles.muted,
    line.tone === 'accent' && styles.accent,
    line.tone === 'success' && styles.success,
    line.tone === 'warning' && styles.warning,
    line.tone === 'error' && styles.error
  );
}

function displayText(line: TerminalLine) {
  if (line.kind === 'tool_use' && line.tool) {
    const summary = typeof line.meta?.summary === 'string' ? line.meta.summary : '';
    return `● ${line.tool}${summary ? ` ${summary}` : ''}`;
  }
  return line.text;
}

export function LogPanel({ log, run }: { log: RunLogState; run?: Run }) {
  const scrollRef = useRef<HTMLPreElement>(null);
  const [filter, setFilter] = useState<FilterKey>('all');
  const [autoScroll, setAutoScroll] = useState(true);
  const [copied, setCopied] = useState(false);

  const visibleLines = useMemo(
    () => log.lines.filter((line) => lineMatches(line, filter)),
    [log.lines, filter]
  );

  useEffect(() => {
    if (!autoScroll || !scrollRef.current) return;
    scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [visibleLines.length, autoScroll]);

  const handleScroll = useCallback(() => {
    if (!scrollRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = scrollRef.current;
    setAutoScroll(scrollHeight - scrollTop - clientHeight < 24);
  }, []);

  const copy = useCallback(async () => {
    const text = log.rawLog || log.lines.map((line) => line.text).join('\n');
    await navigator.clipboard.writeText(text);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1600);
  }, [log.rawLog, log.lines]);

  const download = useCallback(() => {
    const text = log.rawLog || log.lines.map((line) => line.text).join('\n');
    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = `run-${run?.id || 'log'}-${new Date().toISOString().slice(0, 19)}.log`;
    anchor.click();
    URL.revokeObjectURL(url);
  }, [log.rawLog, log.lines, run?.id]);

  return (
    <section className={styles.panel}>
      <div className={styles.header}>
        <h2 className={styles.title}>
          <Terminal size={17} />
          实时日志
          <span className={cn(styles.connection, log.isConnected && styles.connected)} title={log.isConnected ? '已连接' : '未连接'} />
        </h2>
        <div className={styles.actions}>
          <Button variant={autoScroll ? 'secondary' : 'ghost'} onClick={() => setAutoScroll((value) => !value)}>
            {autoScroll ? '自动滚动' : '手动滚动'}
          </Button>
          <Button iconOnly variant="ghost" onClick={copy} title="复制日志">
            {copied ? <Check size={16} /> : <Copy size={16} />}
          </Button>
          <Button iconOnly variant="ghost" onClick={download} title="下载日志">
            <Download size={16} />
          </Button>
        </div>
      </div>
      <div className={styles.filters}>
        {filters.map((item) => (
          <button
            key={item.key}
            className={cn(styles.chip, filter === item.key && styles.chipActive)}
            onClick={() => setFilter(item.key)}
          >
            {item.label}
          </button>
        ))}
      </div>
      <pre className={styles.terminal} ref={scrollRef} onScroll={handleScroll}>
        {visibleLines.length === 0 ? (
          <span className={styles.emptyWrap}>
            <EmptyState
              title={run?.status === 'completed' ? '任务已完成' : '等待事件...'}
              description={run ? '日志流连接后会显示 Codex 终端事件' : '请选择一个任务'}
              icon={Terminal}
            />
          </span>
        ) : (
          visibleLines.map((line, index) => (
            <span key={line.id || index} className={lineClass(line)}>
              <span className={styles.lineNo}>{index + 1}</span>
              <span className={styles.content}>
                {line.kind === 'todo' ? (
                  <span className={styles.todoText}>
                    <span className={styles.todoGlyph}>{todoGlyph(line.status)}</span>
                    {line.text}
                  </span>
                ) : (
                  displayText(line)
                )}
              </span>
            </span>
          ))
        )}
      </pre>
    </section>
  );
}
