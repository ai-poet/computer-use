import { useCallback, useEffect, useMemo, useState } from 'react';
import { createRun, getReport, getRun, listRuns } from '../../shared/lib/api';
import type { CreateRunPayload, Run, RunDetail } from './types';

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

  const refreshRuns = useCallback(async (preferredId?: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await listRuns();
      setRuns(data);
      const nextSelected = preferredId || selected;
      if (nextSelected && data.some((run) => run.id === nextSelected)) {
        setSelected(nextSelected);
      } else if (!nextSelected && data.length) {
        setSelected(data[0].id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载任务列表失败');
    } finally {
      setIsLoading(false);
    }
  }, [selected]);

  const refreshDetail = useCallback(async (runId = selected) => {
    if (!runId) {
      setDetail(null);
      setReport('');
      return;
    }
    try {
      const [nextDetail, nextReport] = await Promise.all([
        getRun(runId),
        getReport(runId)
      ]);
      setDetail(nextDetail);
      setReport(nextReport);
    } catch (err) {
      console.error('Failed to refresh detail:', err);
    }
  }, [selected]);

  const startRun = useCallback(async (payload: CreateRunPayload) => {
    setError(null);
    const created = await createRun(payload);
    setSelected(created.id);
    await refreshRuns(created.id);
    await refreshDetail(created.id);
    return created;
  }, [refreshRuns, refreshDetail]);

  useEffect(() => {
    void refreshRuns();
  }, []);

  useEffect(() => {
    if (!selected) return;
    void refreshDetail(selected);
    const detailTimer = window.setInterval(() => void refreshDetail(selected), 3000);
    const listTimer = window.setInterval(() => void refreshRuns(selected), 5000);
    return () => {
      window.clearInterval(detailTimer);
      window.clearInterval(listTimer);
    };
  }, [selected, refreshDetail, refreshRuns]);

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
