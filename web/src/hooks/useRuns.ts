import { useEffect, useMemo, useState } from 'react';
import { createRun, getReport, getRun, listRuns } from '../api';
import type { CreateRunPayload, Run, RunDetail } from '../types';

export function useRuns() {
  const [runs, setRuns] = useState<Run[]>([]);
  const [selected, setSelected] = useState('');
  const [detail, setDetail] = useState<RunDetail | null>(null);
  const [report, setReport] = useState('');

  const selectedRun = useMemo(
    () => runs.find((run) => run.id === selected),
    [runs, selected]
  );

  async function refreshRuns() {
    const data = await listRuns();
    setRuns(data);
    if (!selected && data.length) setSelected(data[0].id);
  }

  async function refreshDetail(runId = selected) {
    if (!runId) return;
    setDetail(await getRun(runId));
    setReport(await getReport(runId));
  }

  async function startRun(payload: CreateRunPayload) {
    await createRun(payload);
    await refreshRuns();
  }

  useEffect(() => {
    void refreshRuns();
  }, []);

  useEffect(() => {
    if (!selected) return;
    void refreshDetail(selected);
    const timer = window.setInterval(() => void refreshDetail(selected), 3000);
    return () => window.clearInterval(timer);
  }, [selected]);

  return {
    runs,
    selected,
    selectedRun,
    detail,
    report,
    setSelected,
    refreshRuns,
    startRun
  };
}
