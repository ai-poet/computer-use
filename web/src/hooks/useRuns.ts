import { useEffect, useMemo, useState, useCallback } from 'react';
import { createRun, getReport, getRun, listRuns } from '../api';
import type { CreateRunPayload, Run, RunDetail } from '../types';

export function useRuns() {
  const [runs, setRuns] = useState<Run[]>([]);
  const [selected, setSelected] = useState('');
  const [detail, setDetail] = useState<RunDetail | null>(null);
  const [report, setReport] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const selectedRun = useMemo(
    () => runs.find((run) => run.id === selected),
    [runs, selected]
  );

  const refreshRuns = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await listRuns();
      setRuns(data);
      if (!selected && data.length) setSelected(data[0].id);
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载任务列表失败');
    } finally {
      setIsLoading(false);
    }
  }, [selected]);

  const refreshDetail = useCallback(async (runId = selected) => {
    if (!runId) return;
    try {
      setDetail(await getRun(runId));
      setReport(await getReport(runId));
    } catch (err) {
      console.error('Failed to refresh detail:', err);
    }
  }, [selected]);

  const startRun = useCallback(async (payload: CreateRunPayload) => {
    setError(null);
    try {
      await createRun(payload);
      await refreshRuns();
    } catch (err) {
      setError(err instanceof Error ? err.message : '创建任务失败');
      throw err;
    }
  }, [refreshRuns]);

  useEffect(() => {
    void refreshRuns();
  }, []);

  useEffect(() => {
    if (!selected) return;
    void refreshDetail(selected);
    const timer = window.setInterval(() => void refreshDetail(selected), 3000);
    return () => window.clearInterval(timer);
  }, [selected, refreshDetail]);

  return {
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
  };
}
