import { Pause, Play } from 'lucide-react';
import type { Run } from '../types';

export function TopBar({ run }: { run?: Run }) {
  return (
    <header className="topbar">
      <div>
        <h1>{run?.product_name || 'Product Analyzer'}</h1>
        <p>{run?.url || '本地 Linux-first 产品分析控制台'}</p>
      </div>
      <div className="actions">
        <button disabled>
          <Pause size={16} />
          暂停
        </button>
        <button disabled>
          <Play size={16} />
          继续
        </button>
      </div>
    </header>
  );
}
