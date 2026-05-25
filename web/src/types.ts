export type Run = {
  id: string;
  product_name: string;
  url?: string;
  mode?: string | null;
  runtime?: string | null;
  queue?: {
    category?: string | null;
    file?: string | null;
  } | null;
  finished_at?: string | null;
  current_step?: string | null;
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
};

export type RunDetail = {
  id: string;
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
