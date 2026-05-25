import { Play, RefreshCcw, ShieldCheck } from 'lucide-react';
import { useState } from 'react';
import type { CreateRunPayload, Run } from '../types';

type Props = {
  runs: Run[];
  selected: string;
  onSelect: (id: string) => void;
  onRefresh: () => void;
  onCreate: (payload: CreateRunPayload) => Promise<void>;
};

export function RunSidebar({ runs, selected, onSelect, onRefresh, onCreate }: Props) {
  const [form, setForm] = useState({ product_name: '', url: '', download_url: '' });

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    await onCreate({
      product_name: form.product_name,
      url: form.url,
      download_url: form.download_url || null,
      sandbox_image: 'linux',
      android: true
    });
    setForm({ product_name: '', url: '', download_url: '' });
  }

  return (
    <aside className="sidebar">
      <div className="brand">
        <ShieldCheck size={22} />
        <span>Analyzer</span>
      </div>
      <form className="new-run" onSubmit={submit}>
        <input
          placeholder="产品名"
          value={form.product_name}
          onChange={(e) => setForm({ ...form, product_name: e.target.value })}
          required
        />
        <input
          placeholder="官网 URL"
          value={form.url}
          onChange={(e) => setForm({ ...form, url: e.target.value })}
          required
        />
        <input
          placeholder="下载链接，可选"
          value={form.download_url}
          onChange={(e) => setForm({ ...form, download_url: e.target.value })}
        />
        <button type="submit">
          <Play size={16} />
          新建
        </button>
      </form>
      <button className="ghost" onClick={onRefresh}>
        <RefreshCcw size={16} />
        刷新
      </button>
      <div className="run-list">
        {runs.map((run) => (
          <button
            className={run.id === selected ? 'run active' : 'run'}
            key={run.id}
            onClick={() => onSelect(run.id)}
          >
            <strong>{run.product_name}</strong>
            <small>{run.current_step || run.mode || 'starting'}</small>
          </button>
        ))}
      </div>
    </aside>
  );
}
