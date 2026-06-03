import type {
  CreateBatchRunsPayload,
  CreateBatchRunsResponse,
  CreateRunPayload,
  CreateRunResponse,
  Run,
  RunDetail
} from '../../features/runs/types';
import type { Screenshot } from '../../features/report/types';

function runPath(runId: string): string {
  return encodeURIComponent(runId);
}

async function errorMessage(res: Response, fallback: string): Promise<string> {
  try {
    const data = await res.json();
    return data?.detail?.error || data?.detail?.detail || data?.error || fallback;
  } catch {
    return fallback;
  }
}

export async function listRuns(): Promise<Run[]> {
  const res = await fetch('/api/runs');
  if (!res.ok) throw new Error(await errorMessage(res, 'failed to list runs'));
  return (await res.json()) as Run[];
}

export async function createRun(payload: CreateRunPayload): Promise<CreateRunResponse> {
  const res = await fetch('/api/runs', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error(await errorMessage(res, 'failed to create run'));
  return (await res.json()) as CreateRunResponse;
}

export async function createBatchRuns(payload: CreateBatchRunsPayload): Promise<CreateBatchRunsResponse> {
  const res = await fetch('/api/runs/batch', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error(await errorMessage(res, 'failed to create batch runs'));
  return (await res.json()) as CreateBatchRunsResponse;
}

export async function getRun(runId: string): Promise<RunDetail> {
  const res = await fetch(`/api/runs/${runPath(runId)}`);
  if (!res.ok) throw new Error(await errorMessage(res, 'failed to load run'));
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
      label: filename.replace(/\.(png|jpg|jpeg|gif|webp)$/i, '').replace(/^\d+_/, '')
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
  if (!res.ok) throw new Error(await errorMessage(res, 'failed to submit credential'));
}

export function screenshotUrl(runId: string, src: string): string {
  const name = src.replace(/^\.?\//, '').replace(/^screenshots\//, '');
  return `/api/runs/${runPath(runId)}/screenshots/${encodeURIComponent(name)}`;
}
