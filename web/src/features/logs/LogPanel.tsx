import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import type { Run } from '../runs/types';
import type { RunLogState } from './types';
import { LogFilters } from './LogFilters';
import { LogToolbar } from './LogToolbar';
import { TerminalViewport } from './TerminalViewport';
import { lineMatches, logTextForExport } from './logModel';
import type { LogFilterKey } from './logModel';
import styles from './LogPanel.module.less';

export function LogPanel({ log, run }: { log: RunLogState; run?: Run }) {
  const scrollRef = useRef<HTMLPreElement>(null);
  const [filter, setFilter] = useState<LogFilterKey>('all');
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
    await navigator.clipboard.writeText(logTextForExport(log));
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1600);
  }, [log]);

  const download = useCallback(() => {
    const blob = new Blob([logTextForExport(log)], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = `run-${run?.id || 'log'}-${new Date().toISOString().slice(0, 19)}.log`;
    anchor.click();
    URL.revokeObjectURL(url);
  }, [log, run?.id]);

  return (
    <section className={styles.panel}>
      <LogToolbar
        connected={log.isConnected}
        autoScroll={autoScroll}
        copied={copied}
        onToggleAutoScroll={() => setAutoScroll((value) => !value)}
        onCopy={copy}
        onDownload={download}
      />
      <LogFilters value={filter} onChange={setFilter} />
      <TerminalViewport lines={visibleLines} run={run} scrollRef={scrollRef} onScroll={handleScroll} />
    </section>
  );
}
