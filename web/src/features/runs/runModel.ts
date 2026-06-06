import type { CreateRunPayload, Run, RunStatus } from './types';

export type RunDraft = {
  product_name: string;
  url: string;
  download_url: string;
  email_provider: string;
  email_address: string;
};

export type RunValidationErrors = Partial<Record<keyof RunDraft, string>>;

export type RunFilterState = {
  search: string;
  status: RunStatus | 'all';
  category: string;
};

export const EMPTY_RUN_DRAFT: RunDraft = {
  product_name: '',
  url: '',
  download_url: '',
  email_provider: '',
  email_address: ''
};

export const DEFAULT_RUN_FILTERS: RunFilterState = {
  search: '',
  status: 'all',
  category: 'all'
};

export const RUN_STATUS_FILTERS: Array<{ key: RunStatus | 'all'; label: string }> = [
  { key: 'all', label: '全部' },
  { key: 'running', label: '运行中' },
  { key: 'completed', label: '已完成' },
  { key: 'failed', label: '失败' }
];

const HTTP_URL_RE = /^https?:\/\/\S+$/i;

export function formatRunDate(value?: string | null): string {
  if (!value) return '';
  return new Date(value).toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' });
}

export function collectRunCategories(runs: Run[]): string[] {
  const categories = new Set<string>();
  runs.forEach((run) => {
    if (run.queue?.category) categories.add(run.queue.category);
  });
  return Array.from(categories).sort();
}

export function filterRuns(runs: Run[], filters: RunFilterState): Run[] {
  const query = filters.search.trim().toLowerCase();

  return runs.filter((run) => {
    if (query && !run.product_name.toLowerCase().includes(query)) return false;
    if (filters.status !== 'all' && run.status !== filters.status) return false;
    if (filters.category !== 'all' && run.queue?.category !== filters.category) return false;
    return true;
  });
}

export function validateRunDraft(draft: RunDraft): RunValidationErrors {
  const errors: RunValidationErrors = {};
  const productName = draft.product_name.trim();
  const url = draft.url.trim();
  const downloadUrl = draft.download_url.trim();

  if (!productName) {
    errors.product_name = '产品名不能为空';
  } else if (productName.length > 80) {
    errors.product_name = '产品名不能超过 80 字符';
  }

  if (!url) {
    errors.url = '官网 URL 不能为空';
  } else if (!HTTP_URL_RE.test(url)) {
    errors.url = '请输入有效 URL';
  }

  if (downloadUrl && !HTTP_URL_RE.test(downloadUrl)) {
    errors.download_url = '请输入有效下载链接';
  }

  return errors;
}

export function hasValidationErrors(errors: RunValidationErrors): boolean {
  return Object.keys(errors).length > 0;
}

export function toCreateRunPayload(draft: RunDraft): CreateRunPayload {
  const overrides: Record<string, string> = {};
  if (draft.email_provider.trim()) overrides.provider = draft.email_provider.trim();
  if (draft.email_address.trim()) overrides.email_address = draft.email_address.trim();

  return {
    product_name: draft.product_name.trim(),
    url: draft.url.trim(),
    download_url: draft.download_url.trim() || null,
    sandbox_image: 'linux',
    android: true,
    email_overrides: Object.keys(overrides).length ? overrides : null
  };
}
