import { useEffect } from 'react';
import { CredentialPanel } from '../../features/credentials/CredentialPanel';
import { LogPanel } from '../../features/logs/LogPanel';
import { useRunStream } from '../../features/logs/useRunStream';
import { ReportPanel } from '../../features/report/ReportPanel';
import { RunSidebar } from '../../features/runs/RunSidebar';
import { useRuns } from '../../features/runs/useRuns';
import { WorkflowPanel } from '../../features/workflow/WorkflowPanel';
import { TopBar } from './TopBar';
import { useTheme } from '../../app/theme';
import styles from './ConsolePage.module.less';

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
    startRun,
    startBatch
  } = useRuns();
  const log = useRunStream(selected);
  const { isDark, toggle } = useTheme();

  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toLowerCase() === 'l') {
        e.preventDefault();
        toggle();
      }
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'r' && !e.shiftKey) {
        e.preventDefault();
        void refreshRuns(selected);
      }
    }
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [toggle, refreshRuns, selected]);

  return (
    <div className={styles.app}>
      <RunSidebar
        runs={runs}
        selected={selected}
        onSelect={setSelected}
        onRefresh={() => void refreshRuns(selected, { silent: true })}
        onCreate={startRun}
        onCreateBatch={startBatch}
        isLoading={isLoading}
      />
      <main className={styles.main}>
        <TopBar
          run={selectedRun}
          isDark={isDark}
          onToggleTheme={toggle}
          onRefresh={() => void refreshRuns(selected, { silent: true })}
        />
        {error ? (
          <div className={styles.error}>{error}</div>
        ) : (
          <section className={styles.workspace}>
            <div className={styles.sideColumn}>
              <WorkflowPanel steps={detail?.workflow.steps || []} />
              <CredentialPanel detail={detail} runId={selected} />
            </div>
            <div className={styles.logs}>
              <LogPanel log={log} run={selectedRun} />
            </div>
            <div className={styles.report}>
              <ReportPanel report={report} runId={selected} />
            </div>
          </section>
        )}
      </main>
    </div>
  );
}
