import { CredentialPanel } from '../components/CredentialPanel';
import { LogPanel } from '../components/LogPanel';
import { ReportPanel } from '../components/ReportPanel';
import { RunSidebar } from '../components/RunSidebar';
import { TopBar } from '../components/TopBar';
import { WorkflowPanel } from '../components/WorkflowPanel';
import { useRuns } from '../hooks/useRuns';
import { useRunStream } from '../hooks/useRunStream';

export function ConsolePage() {
  const {
    runs,
    selected,
    selectedRun,
    detail,
    report,
    setSelected,
    refreshRuns,
    startRun
  } = useRuns();
  const log = useRunStream(selected);

  return (
    <div className="app">
      <RunSidebar
        runs={runs}
        selected={selected}
        onSelect={setSelected}
        onRefresh={refreshRuns}
        onCreate={startRun}
      />
      <main className="main">
        <TopBar run={selectedRun} />
        <section className="grid">
          <WorkflowPanel steps={detail?.workflow.steps || []} />
          <LogPanel log={log} />
          <CredentialPanel detail={detail} runId={selected} />
          <ReportPanel report={report} />
        </section>
      </main>
    </div>
  );
}
