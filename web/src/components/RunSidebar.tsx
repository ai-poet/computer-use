import { useState, useMemo } from 'react';
import {
  Play,
  RefreshCw,
  ShieldCheck,
  Search,
  ChevronDown,
  ChevronUp,
  CheckCircle2,
  XCircle,
  Clock,
  Loader2
} from 'lucide-react';
import { EmptyState } from './EmptyState';
import { LoadingState } from './LoadingState';
import type { CreateRunPayload, Run, RunStatus } from '../types';

type Props = {
  runs: Run[];
  selected: string;
  onSelect: (id: string) => void;
  onRefresh: () => void;
  onCreate: (payload: CreateRunPayload) => Promise<void>;
  isLoading?: boolean;
};

function inferStatus(run: Run): RunStatus {
  if (run.status) return run.status;
  if (run.finished_at) return 'completed';
  if (run.current_step) return 'running';
  return 'pending';
}

const statusColor: Record<RunStatus, string> = {
  running: 'bg-primary-500',
  pending: 'bg-text-tertiary',
  completed: 'bg-success-500',
  failed: 'bg-error-500',
  paused: 'bg-warning-500',
  cancelled: 'bg-text-tertiary'
};

export function RunSidebar({ runs, selected, onSelect, onRefresh, onCreate, isLoading }: Props) {
  const [form, setForm] = useState({ product_name: '', url: '', download_url: '' });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState<RunStatus | 'all'>('all');
  const [showAdvanced, setShowAdvanced] = useState(false);

  const filteredRuns = useMemo(() => {
    let result = runs;
    if (search.trim()) {
      const q = search.toLowerCase();
      result = result.filter((r) => r.product_name.toLowerCase().includes(q));
    }
    if (filter !== 'all') {
      result = result.filter((r) => inferStatus(r) === filter);
    }
    return result;
  }, [runs, search, filter]);

  function validate(): boolean {
    const e: Record<string, string> = {};
    if (!form.product_name.trim()) {
      e.product_name = '产品名不能为空';
    } else if (form.product_name.length > 80) {
      e.product_name = '产品名不能超过80字符';
    }
    if (!form.url.trim()) {
      e.url = '官网 URL 不能为空';
    } else if (!/^https?:\/\/.+/.test(form.url)) {
      e.url = '请输入有效的 URL（以 https:// 开头）';
    }
    if (form.download_url && !/^https?:\/\/.+/.test(form.download_url)) {
      e.download_url = '请输入有效的下载链接';
    }
    setErrors(e);
    return Object.keys(e).length === 0;
  }

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    if (!validate()) return;
    setSubmitting(true);
    try {
      await onCreate({
        product_name: form.product_name,
        url: form.url,
        download_url: form.download_url || null,
        sandbox_image: 'linux',
        android: true
      });
      setForm({ product_name: '', url: '', download_url: '' });
      setErrors({});
    } finally {
      setSubmitting(false);
    }
  }

  const filters: { key: RunStatus | 'all'; label: string }[] = [
    { key: 'all', label: '全部' },
    { key: 'running', label: '运行中' },
    { key: 'completed', label: '已完成' },
    { key: 'failed', label: '失败' }
  ];

  return (
    <aside className="sidebar">
      {/* Brand */}
      <div className="brand">
        <ShieldCheck size={22} className="text-primary-500" />
        <span>Analyzer</span>
        <span className="ml-auto text-xs text-text-tertiary font-normal">v1.0</span>
      </div>

      {/* New run form */}
      <form className="new-run" onSubmit={submit}>
        <div>
          <label className="block text-xs font-medium text-text-secondary mb-1">
            产品名 <span className="text-error-500">*</span>
          </label>
          <input
            placeholder="输入产品名称"
            value={form.product_name}
            onChange={(e) => setForm({ ...form, product_name: e.target.value })}
            onBlur={() => validate()}
            className={`w-full min-h-[36px] border rounded-md px-3 text-sm bg-surface transition-colors ${
              errors.product_name ? 'border-error-500' : 'border-border-default'
            }`}
          />
          <div className="flex justify-between mt-1">
            {errors.product_name ? (
              <span className="text-xs text-error-500">{errors.product_name}</span>
            ) : (
              <span />
            )}
            <span className={`text-xs ${form.product_name.length > 80 ? 'text-error-500' : 'text-text-tertiary'}`}>
              {form.product_name.length}/80
            </span>
          </div>
        </div>

        <div>
          <label className="block text-xs font-medium text-text-secondary mb-1">
            官网 URL <span className="text-error-500">*</span>
          </label>
          <input
            placeholder="https://example.com"
            value={form.url}
            onChange={(e) => setForm({ ...form, url: e.target.value })}
            onBlur={() => validate()}
            className={`w-full min-h-[36px] border rounded-md px-3 text-sm bg-surface transition-colors ${
              errors.url ? 'border-error-500' : 'border-border-default'
            }`}
          />
          {errors.url && <span className="text-xs text-error-500 mt-1 block">{errors.url}</span>}
        </div>

        <button
          type="button"
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="flex items-center gap-1 text-xs text-text-tertiary hover:text-text-secondary transition-colors"
        >
          {showAdvanced ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
          高级选项
        </button>

        {showAdvanced && (
          <div className="animate-fade-in-up">
            <label className="block text-xs font-medium text-text-secondary mb-1">
              下载链接（可选）
            </label>
            <input
              placeholder="直接指向安装包的 URL"
              value={form.download_url}
              onChange={(e) => setForm({ ...form, download_url: e.target.value })}
              className={`w-full min-h-[36px] border rounded-md px-3 text-sm bg-surface transition-colors ${
                errors.download_url ? 'border-error-500' : 'border-border-default'
              }`}
            />
            {errors.download_url && (
              <span className="text-xs text-error-500 mt-1 block">{errors.download_url}</span>
            )}
          </div>
        )}

        <button
          type="submit"
          disabled={submitting}
          className="w-full py-2 bg-primary-500 text-white rounded-md text-sm font-medium hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all inline-flex items-center justify-center gap-2"
        >
          {submitting ? <Loader2 size={16} className="animate-spin" /> : <Play size={16} />}
          {submitting ? '提交中...' : '新建分析'}
        </button>
      </form>

      {/* Search + Filter */}
      <div className="space-y-2">
        <div className="relative">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-tertiary" />
          <input
            placeholder="搜索任务..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full min-h-[32px] pl-8 pr-3 border border-border-default rounded-md text-sm bg-surface"
          />
        </div>
        <div className="flex gap-1 flex-wrap">
          {filters.map((f) => (
            <button
              key={f.key}
              onClick={() => setFilter(f.key)}
              className={`px-2 py-0.5 text-xs rounded-full transition-colors ${
                filter === f.key
                  ? 'bg-primary-50 text-primary-600 border border-primary-200'
                  : 'text-text-tertiary hover:text-text-secondary border border-transparent'
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>
      </div>

      {/* Refresh */}
      <button
        className="ghost inline-flex items-center gap-2 text-sm text-text-secondary hover:text-text-primary transition-colors"
        onClick={onRefresh}
      >
        <RefreshCw size={14} />
        刷新列表
      </button>

      {/* Run list */}
      <div className="run-list flex-1 min-h-0">
        {isLoading ? (
          <LoadingState variant="skeleton-card" count={3} />
        ) : filteredRuns.length === 0 ? (
          search || filter !== 'all' ? (
            <EmptyState
              variant="search"
              title="未找到匹配任务"
              description={`没有符合 "${search}" 的任务`}
              action={{
                label: '清除搜索',
                onClick: () => {
                  setSearch('');
                  setFilter('all');
                }
              }}
            />
          ) : (
            <EmptyState
              variant="empty"
              title="暂无分析任务"
              description={'点击上方"新建分析"按钮开始产品分析'}
            />
          )
        ) : (
          filteredRuns.map((run) => {
            const s = inferStatus(run);
            return (
              <button
                className={`run w-full ${run.id === selected ? 'active' : ''}`}
                key={run.id}
                onClick={() => onSelect(run.id)}
              >
                <div className="flex items-center gap-2 w-full">
                  <span className={`w-2 h-2 rounded-full flex-shrink-0 ${statusColor[s]}`} />
                  <strong className="text-sm text-text-primary truncate flex-1 text-left">
                    {run.product_name}
                  </strong>
                  {run.created_at && (
                    <span className="text-xs text-text-tertiary flex items-center gap-0.5 flex-shrink-0">
                      <Clock size={10} />
                      {new Date(run.created_at).toLocaleDateString('zh-CN')}
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-2 mt-1 w-full">
                  <small className="text-xs text-text-tertiary truncate flex-1 text-left">
                    {run.queue?.category ? `${run.queue.category} · ` : ''}
                    {run.current_step || run.mode || 'starting'}
                  </small>
                  {s === 'completed' && <CheckCircle2 size={12} className="text-success-500 flex-shrink-0" />}
                  {s === 'failed' && <XCircle size={12} className="text-error-500 flex-shrink-0" />}
                </div>
              </button>
            );
          })
        )}
      </div>
    </aside>
  );
}
