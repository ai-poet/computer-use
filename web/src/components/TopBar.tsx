import { Pause, Play, RefreshCw, Sun, Moon } from 'lucide-react';
import { StatusBadge } from './StatusBadge';
import type { Run, RunStatus } from '../types';

interface TopBarProps {
  run?: Run;
  onToggleTheme?: () => void;
  isDark?: boolean;
  onRefresh?: () => void;
}

function inferStatus(run?: Run): RunStatus {
  if (!run) return 'pending';
  if (run.status) return run.status;
  if (run.finished_at) return 'completed';
  if (run.current_step) return 'running';
  return 'pending';
}

export function TopBar({ run, onToggleTheme, isDark, onRefresh }: TopBarProps) {
  const status = inferStatus(run);
  const isRunning = status === 'running';

  return (
    <header className="topbar relative">
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-3 mb-0.5">
          <h1 className="text-xl font-semibold text-text-primary truncate">
            {run?.product_name || 'Product Analyzer'}
          </h1>
          {run && <StatusBadge status={status} size="sm" pulse={isRunning} />}
        </div>
        {run?.url && (
          <p
            className="text-sm text-text-secondary truncate max-w-xl"
            title={run.url}
          >
            {run.url}
          </p>
        )}
        {!run?.url && (
          <p className="text-sm text-text-secondary">本地 Linux-first 产品分析控制台</p>
        )}
      </div>

      <div className="actions flex-shrink-0">
        {onToggleTheme && (
          <button
            onClick={onToggleTheme}
            className="p-2 rounded-md hover:bg-bg-secondary transition-colors"
            title={isDark ? '切换到亮色模式' : '切换到暗色模式'}
          >
            {isDark ? <Sun size={18} /> : <Moon size={18} />}
          </button>
        )}
        {onRefresh && (
          <button
            onClick={onRefresh}
            className="p-2 rounded-md hover:bg-bg-secondary transition-colors"
            title="刷新"
          >
            <RefreshCw size={18} />
          </button>
        )}
        <button
          disabled={!isRunning}
          className="px-3 py-1.5 text-sm rounded-md border border-border-subtle hover:bg-bg-secondary disabled:opacity-40 disabled:cursor-not-allowed transition-all inline-flex items-center gap-1.5"
        >
          <Pause size={14} />
          暂停
        </button>
        <button
          disabled={status !== 'paused'}
          className="px-3 py-1.5 text-sm rounded-md border border-border-subtle hover:bg-bg-secondary disabled:opacity-40 disabled:cursor-not-allowed transition-all inline-flex items-center gap-1.5"
        >
          <Play size={14} />
          继续
        </button>
      </div>

      {/* Progress bar */}
      {isRunning && (
        <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-bg-secondary">
          <div className="h-full bg-primary-500 animate-pulse" style={{ width: '60%' }} />
        </div>
      )}
    </header>
  );
}
