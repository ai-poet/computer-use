export type RunStatus = 'running' | 'pending' | 'completed' | 'failed' | 'paused' | 'cancelled';

export type RunProgress = {
  completed: number;
  total: number;
  percent: number;
};

export type Run = {
  id: string;
  out_dir?: string;
  product_name: string;
  url?: string;
  mode?: string | null;
  runtime?: string | null;
  queue?: {
    category?: string | null;
    file?: string | null;
  } | null;
  status: RunStatus;
  started_at?: string | null;
  finished_at?: string | null;
  current_step?: string | null;
  progress?: RunProgress;
};

export type WorkflowStep = {
  id: string;
  title: string;
  file: string;
  status: string;
  summary?: string | null;
};

export type CredentialRequest = {
  id?: string;
  service?: string;
  reason?: string;
  status?: string;
  fields?: string[];
};

export type RunDetail = {
  id: string;
  out_dir?: string;
  metadata: Record<string, unknown>;
  workflow: {
    steps?: WorkflowStep[];
    credential_requests?: CredentialRequest[];
  };
};

export type CreateRunPayload = {
  product_name: string;
  url: string;
  download_url?: string | null;
  sandbox_image: string;
  android: boolean;
};

export type CreateRunResponse = {
  id: string;
  state: 'starting';
  warnings: string[];
};

export type BatchRunInput = {
  product_name: string;
  url: string;
  download_url?: string | null;
  category?: string | null;
};

export type CreateBatchRunsPayload = {
  rows: BatchRunInput[];
  max_workers: number;
  queue_name?: string | null;
  sandbox_image: string;
  android: boolean;
};

export type CreateBatchRunsResponse = {
  batch_id: string;
  ids: string[];
  state: 'starting';
  warnings: string[];
};
