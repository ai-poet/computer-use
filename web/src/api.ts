import type { CreateRunPayload, Run, RunDetail } from './types';

export async function listRuns(): Promise<Run[]> {
  const res = await fetch('/api/runs');
  if (!res.ok) throw new Error('failed to list runs');
  return (await res.json()) as Run[];
}

export async function createRun(payload: CreateRunPayload): Promise<void> {
  const res = await fetch('/api/runs', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error('failed to create run');
}

export async function getRun(runId: string): Promise<RunDetail> {
  const res = await fetch(`/api/runs/${runId}`);
  if (!res.ok) throw new Error('failed to load run');
  return (await res.json()) as RunDetail;
}

export async function getReport(runId: string): Promise<string> {
  const res = await fetch(`/api/runs/${runId}/report`);
  return res.ok ? await res.text() : '';
}

export async function submitCredential(
  runId: string,
  requestId: string,
  label: string,
  fields: Record<string, string>
): Promise<void> {
  const res = await fetch(`/api/runs/${runId}/credentials`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ request_id: requestId, label, fields })
  });
  if (!res.ok) throw new Error('failed to submit credential');
}
