import { useMemo, useState } from 'react';
import { ChevronDown, ChevronUp, Loader2, Play, RefreshCw, Search, ShieldCheck } from 'lucide-react';
import { Button } from '../../shared/ui/Button';
import { EmptyState } from '../../shared/ui/EmptyState';
import type { CreateRunPayload, Run, RunStatus } from './types';
import styles from './RunSidebar.module.less';
import { cn } from '../../shared/lib/cn';

type Props = {
  runs: Run[];
  selected: string;
  onSelect: (id: string) => void;
  onRefresh: () => void;
  onCreate: (payload: CreateRunPayload) => Promise<unknown>;
  isLoading?: boolean;
};

const filters: Array<{ key: RunStatus | 'all'; label: string }> = [
  { key: 'all', label: '全部' },
  { key: 'running', label: '运行中' },
  { key: 'completed', label: '已完成' },
  { key: 'failed', label: '失败' }
];

function formatDate(value?: string | null): string {
  if (!value) return '';
  return new Date(value).toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' });
}

export function RunSidebar({ runs, selected, onSelect, onRefresh, onCreate, isLoading }: Props) {
  const [form, setForm] = useState({ product_name: '', url: '', download_url: '' });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState<RunStatus | 'all'>('all');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [showAdvanced, setShowAdvanced] = useState(false);

  const categories = useMemo(() => {
    const set = new Set<string>();
    runs.forEach((run) => {
      if (run.queue?.category) set.add(run.queue.category);
    });
    return Array.from(set).sort();
  }, [runs]);

  const filteredRuns = useMemo(() => {
    let result = runs;
    if (search.trim()) {
      const q = search.toLowerCase();
      result = result.filter((run) => run.product_name.toLowerCase().includes(q));
    }
    if (filter !== 'all') result = result.filter((run) => run.status === filter);
    if (categoryFilter !== 'all') {
      result = result.filter((run) => run.queue?.category === categoryFilter);
    }
    return result;
  }, [runs, search, filter, categoryFilter]);

  function validate() {
    const next: Record<string, string> = {};
    if (!form.product_name.trim()) {
      next.product_name = '产品名不能为空';
    } else if (form.product_name.length > 80) {
      next.product_name = '产品名不能超过 80 字符';
    }
    if (!form.url.trim()) {
      next.url = '官网 URL 不能为空';
    } else if (!/^https?:\/\/.+/.test(form.url)) {
      next.url = '请输入有效 URL';
    }
    if (form.download_url && !/^https?:\/\/.+/.test(form.download_url)) {
      next.download_url = '请输入有效下载链接';
    }
    setErrors(next);
    return Object.keys(next).length === 0;
  }

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    if (!validate()) return;
    setSubmitting(true);
    try {
      await onCreate({
        product_name: form.product_name.trim(),
        url: form.url.trim(),
        download_url: form.download_url.trim() || null,
        sandbox_image: 'linux',
        android: true
      });
      setForm({ product_name: '', url: '', download_url: '' });
      setErrors({});
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <aside className={styles.sidebar}>
      <div className={styles.brand}>
        <ShieldCheck size={22} />
        Analyzer
        <span className={styles.version}>v1.0</span>
      </div>

      <form className={styles.form} onSubmit={submit}>
        <label className={styles.field}>
          <span className={styles.label}>产品名</span>
          <input
            className={styles.input}
            value={form.product_name}
            onChange={(event) => setForm({ ...form, product_name: event.target.value })}
            onBlur={validate}
            placeholder="输入产品名称"
          />
          {errors.product_name ? (
            <span className={styles.errorText}>{errors.product_name}</span>
          ) : (
            <span className={styles.charCount}>{form.product_name.length}/80</span>
          )}
        </label>

        <label className={styles.field}>
          <span className={styles.label}>官网 URL</span>
          <input
            className={styles.input}
            value={form.url}
            onChange={(event) => setForm({ ...form, url: event.target.value })}
            onBlur={validate}
            placeholder="https://example.com"
          />
          {errors.url && <span className={styles.errorText}>{errors.url}</span>}
        </label>

        <button
          type="button"
          className={styles.advancedButton}
          onClick={() => setShowAdvanced((value) => !value)}
        >
          {showAdvanced ? <ChevronUp size={13} /> : <ChevronDown size={13} />} 高级选项
        </button>

        {showAdvanced && (
          <label className={cn(styles.field, styles.advanced)}>
            <span className={styles.label}>下载链接（可选）</span>
            <input
              className={styles.input}
              value={form.download_url}
              onChange={(event) => setForm({ ...form, download_url: event.target.value })}
              placeholder="直接指向安装包的 URL"
            />
            {errors.download_url && <span className={styles.errorText}>{errors.download_url}</span>}
          </label>
        )}

        <Button variant="primary" full disabled={submitting}>
          {submitting ? <Loader2 size={15} className="spin" /> : <Play size={15} />}
          {submitting ? '提交中...' : '新建分析'}
        </Button>
      </form>

      <div className={styles.tools}>
        <div className={styles.searchWrap}>
          <Search size={14} className={styles.searchIcon} />
          <input
            className={cn(styles.input, styles.search)}
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="搜索任务..."
          />
        </div>
        <div className={styles.filters}>
          {filters.map((item) => (
            <button
              key={item.key}
              className={cn(styles.chip, filter === item.key && styles.chipActive)}
              onClick={() => setFilter(item.key)}
            >
              {item.label}
            </button>
          ))}
        </div>
        {categories.length > 0 && (
          <div className={styles.filters}>
            <button
              className={cn(styles.chip, categoryFilter === 'all' && styles.chipActive)}
              onClick={() => setCategoryFilter('all')}
            >
              全部种类
            </button>
            {categories.map((category) => (
              <button
                key={category}
                className={cn(styles.chip, categoryFilter === category && styles.chipActive)}
                onClick={() => setCategoryFilter(category)}
              >
                {category}
              </button>
            ))}
          </div>
        )}
        <Button variant="ghost" onClick={onRefresh}>
          <RefreshCw size={14} />
          刷新列表
        </Button>
      </div>

      <div className={styles.list}>
        {isLoading ? (
          <div className={styles.loading}>
            <div className={styles.skeleton} />
            <div className={styles.skeleton} />
            <div className={styles.skeleton} />
          </div>
        ) : filteredRuns.length === 0 ? (
          <EmptyState title="暂无任务" description="创建一次分析后，这里会显示任务进度" />
        ) : (
          filteredRuns.map((run) => (
            <button
              key={run.id}
              className={cn(styles.run, run.id === selected && styles.runActive)}
              onClick={() => onSelect(run.id)}
            >
              <div className={styles.runTop}>
                <span className={cn(styles.statusDot, styles[run.status])} />
                <span className={styles.name}>{run.product_name}</span>
                <span className={styles.date}>{formatDate(run.started_at)}</span>
              </div>
              <div className={styles.meta}>
                <span className={styles.metaText}>
                  {run.queue?.category ? `${run.queue.category} · ` : ''}
                  {run.current_step || run.mode || run.status}
                </span>
                {run.progress && run.progress.total > 0 && (
                  <span className={styles.progress} title={`${run.progress.percent}%`}>
                    <span className={styles.progressFill} style={{ width: `${run.progress.percent}%` }} />
                  </span>
                )}
              </div>
            </button>
          ))
        )}
      </div>
    </aside>
  );
}
