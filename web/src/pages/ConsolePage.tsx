import { useState, useEffect, useCallback } from 'react';
import { CredentialPanel } from '../components/CredentialPanel';
import { LogPanel } from '../components/LogPanel';
import { ReportPanel } from '../components/ReportPanel';
import { RunSidebar } from '../components/RunSidebar';
import { TopBar } from '../components/TopBar';
import { WorkflowPanel } from '../components/WorkflowPanel';
import { ErrorState } from '../components/ErrorState';
import { useRuns } from '../hooks/useRuns';
import { useRunStream } from '../hooks/useRunStream';

function useTheme() {
  const [isDark, setIsDark] = useState(() => {
    const saved = localStorage.getItem('theme');
    if (saved === 'dark') return true;
    if (saved === 'light') return false;
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  useEffect(() => {
    const root = document.documentElement;
    if (isDark) {
      root.setAttribute('data-theme', 'dark');
    } else {
      root.removeAttribute('data-theme');
    }
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
  }, [isDark]);

  const toggle = useCallback(() => setIsDark((d) => !d), []);

  return { isDark, toggle };
}

export function ConsolePage() {
  const {
    runs,
    selected,
    selectedRun,
    detail,
    report,
    isLoading,
    error,
    setSelected,
    refreshRuns,
    startRun
  } = useRuns();
  const log = useRunStream(selected);
  const { isDark, toggle } = useTheme();

  // Keyboard shortcuts
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      // Ctrl/Cmd + Shift + L: toggle theme
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'L') {
        e.preventDefault();
        toggle();
      }
      // Ctrl/Cmd + R: refresh
      if ((e.ctrlKey || e.metaKey) && e.key === 'r' && !e.shiftKey) {
        e.preventDefault();
        void refreshRuns();
      }
    }
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [toggle, refreshRuns]);

  return (
    <div className="app">
      <RunSidebar
        runs={runs}
        selected={selected}
        onSelect={setSelected}
        onRefresh={refreshRuns}
        onCreate={startRun}
        isLoading={isLoading}
      />
      <main className="main">
        <TopBar
          run={selectedRun}
          onToggleTheme={toggle}
          isDark={isDark}
          onRefresh={refreshRuns}
        />
        {error ? (
          <ErrorState
            title="加载失败"
            message={error}
            onRetry={refreshRuns}
            className="m-8"
          />
        ) : (
          <section className="grid">
            <WorkflowPanel steps={detail?.workflow.steps || []} />
            <LogPanel log={log} />
            <CredentialPanel detail={detail} runId={selected} />
            <ReportPanel report={report} runId={selected} />
          </section>
        )}
      </main>
    </div>
  );
}
