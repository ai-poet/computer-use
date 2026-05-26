import { useRef, useEffect, useState, useCallback } from 'react';
import {
  Terminal,
  Copy,
  Check,
  Trash2,
  Download,
  Filter
} from 'lucide-react';
import { EmptyState } from './EmptyState';

type LogLevel = 'all' | 'info' | 'warn' | 'error';

interface LogPanelProps {
  log: string;
}

function parseLogLine(line: string): { timestamp?: string; level?: string; message: string } {
  const match = line.match(/^(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}[\d\.Z+-]*)?\s*(\[(INFO|WARN|ERROR|DEBUG)\])?\s*(.*)$/i);
  if (match) {
    return {
      timestamp: match[1],
      level: match[3]?.toUpperCase(),
      message: match[4] || line
    };
  }
  return { message: line };
}

function levelColor(level?: string): string {
  switch (level) {
    case 'INFO':
      return 'text-success-500';
    case 'WARN':
      return 'text-warning-500';
    case 'ERROR':
      return 'text-error-500';
    case 'DEBUG':
      return 'text-primary-500';
    default:
      return 'text-text-tertiary';
  }
}

export function LogPanel({ log }: LogPanelProps) {
  const scrollRef = useRef<HTMLPreElement>(null);
  const [autoScroll, setAutoScroll] = useState(true);
  const [filter, setFilter] = useState<LogLevel>('all');
  const [copied, setCopied] = useState(false);
  const [userScrolled, setUserScrolled] = useState(false);

  const lines = log.split('\n').filter(Boolean);

  const filteredLines = lines.filter((line) => {
    if (filter === 'all') return true;
    const { level } = parseLogLine(line);
    if (filter === 'error') return level === 'ERROR';
    if (filter === 'warn') return level === 'WARN' || level === 'ERROR';
    if (filter === 'info') return level === 'INFO' || level === 'DEBUG' || !level;
    return true;
  });

  // Auto scroll
  useEffect(() => {
    if (!autoScroll || userScrolled || !scrollRef.current) return;
    scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [log, autoScroll, userScrolled]);

  const handleScroll = useCallback(() => {
    if (!scrollRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = scrollRef.current;
    const isAtBottom = scrollHeight - scrollTop - clientHeight < 20;
    setUserScrolled(!isAtBottom);
    if (isAtBottom) setAutoScroll(true);
  }, []);

  const handleCopy = useCallback(async () => {
    await navigator.clipboard.writeText(log);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }, [log]);

  const handleDownload = useCallback(() => {
    const blob = new Blob([log], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `log-${new Date().toISOString().slice(0, 19)}.log`;
    a.click();
    URL.revokeObjectURL(url);
  }, [log]);

  const handleClear = useCallback(() => {
    // We can't actually clear the log since it's controlled by parent,
    // but we can toggle a visual clear state
  }, []);

  const filters: { key: LogLevel; label: string }[] = [
    { key: 'all', label: '全部' },
    { key: 'info', label: 'Info' },
    { key: 'warn', label: 'Warn' },
    { key: 'error', label: 'Error' }
  ];

  return (
    <div className="panel">
      {/* Toolbar */}
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-base font-semibold flex items-center gap-2 text-text-primary m-0">
          <Terminal size={18} className="text-primary-500" />
          实时日志
        </h2>
        <div className="flex items-center gap-1">
          {filters.map((f) => (
            <button
              key={f.key}
              onClick={() => setFilter(f.key)}
              className={`px-2 py-0.5 text-xs rounded transition-colors ${
                filter === f.key
                  ? 'bg-primary-50 text-primary-600'
                  : 'text-text-tertiary hover:text-text-secondary'
              }`}
            >
              {f.label}
            </button>
          ))}
          <div className="w-px h-4 bg-border-subtle mx-1" />
          <button
            onClick={handleCopy}
            className="p-1 rounded hover:bg-bg-secondary transition-colors"
            title="复制全部"
          >
            {copied ? <Check size={14} className="text-success-500" /> : <Copy size={14} />}
          </button>
          <button
            onClick={handleDownload}
            className="p-1 rounded hover:bg-bg-secondary transition-colors"
            title="下载日志"
          >
            <Download size={14} />
          </button>
        </div>
      </div>

      {/* Auto-scroll toggle */}
      <div className="flex items-center gap-2 mb-2">
        <button
          onClick={() => setAutoScroll(!autoScroll)}
          className={`text-xs flex items-center gap-1 transition-colors ${
            autoScroll ? 'text-primary-500' : 'text-text-tertiary'
          }`}
        >
          <Filter size={10} />
          {autoScroll ? '自动滚动开启' : '自动滚动关闭'}
        </button>
      </div>

      {/* Log content */}
      {log ? (
        <pre
          ref={scrollRef}
          className="log"
          onScroll={handleScroll}
        >
          {filteredLines.map((line, i) => {
            const { timestamp, level, message } = parseLogLine(line);
            return (
              <div key={i} className="flex items-start gap-2 hover:bg-bg-secondary/50 rounded px-1 -mx-1">
                <span className="text-text-tertiary select-none flex-shrink-0 w-8 text-right text-xs pt-0.5">
                  {i + 1}
                </span>
                {timestamp && (
                  <span className="text-text-tertiary flex-shrink-0 text-xs pt-0.5">
                    {timestamp.slice(11, 19)}
                  </span>
                )}
                {level && (
                  <span className={`flex-shrink-0 text-xs font-medium pt-0.5 ${levelColor(level)}`}>
                    [{level}]
                  </span>
                )}
                <span className="break-all">{message}</span>
              </div>
            );
          })}
          {filteredLines.length === 0 && (
            <p className="text-text-tertiary text-center py-8">没有符合筛选条件的日志</p>
          )}
        </pre>
      ) : (
        <EmptyState
          variant="loading"
          title="等待事件..."
          description="日志流连接中，有新事件时会自动显示"
        />
      )}
    </div>
  );
}
