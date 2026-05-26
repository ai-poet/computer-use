import type { CreateRunPayload, Run, RunDetail, Screenshot } from './types';

function runPath(runId: string): string {
  return encodeURIComponent(runId);
}

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
  const res = await fetch(`/api/runs/${runPath(runId)}`);
  if (!res.ok) throw new Error('failed to load run');
  return (await res.json()) as RunDetail;
}

export async function getReport(runId: string): Promise<string> {
  const res = await fetch(`/api/runs/${runPath(runId)}/report`);
  return res.ok ? await res.text() : '';
}

export async function listScreenshots(runId: string): Promise<Screenshot[]> {
  const res = await fetch(`/api/runs/${runPath(runId)}/screenshots`);
  if (!res.ok) return [];
  const filenames: string[] = await res.json();
  return filenames.map((filename, index) => {
    const source: Screenshot['source'] = filename.includes('_app_')
      ? 'app'
      : filename.includes('_android_')
        ? 'android'
        : 'web';
    return {
      id: `${runId}-${index}`,
      filename,
      url: `/api/runs/${runPath(runId)}/screenshots/${encodeURIComponent(filename)}`,
      source,
      label: filename.replace(/\.png$/i, '').replace(/\d+_/, '')
    };
  });
}

export async function submitCredential(
  runId: string,
  requestId: string,
  label: string,
  fields: Record<string, string>
): Promise<void> {
  const res = await fetch(`/api/runs/${runPath(runId)}/credentials`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ request_id: requestId, label, fields })
  });
  if (!res.ok) throw new Error('failed to submit credential');
}
