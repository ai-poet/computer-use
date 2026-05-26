import { CheckCircle2, Circle, Pause, Play, XCircle } from 'lucide-react';
import type { RunStatus } from '../types';

interface StatusBadgeProps {
  status: RunStatus;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  pulse?: boolean;
}

const statusConfig: Record<RunStatus, { label: string; color: string; icon: React.ReactNode }> = {
  running: {
    label: '运行中',
    color: 'text-primary-500 bg-primary-50 border-primary-200',
    icon: <Play size={12} fill="currentColor" />
  },
  pending: {
    label: '等待中',
    color: 'text-text-tertiary bg-bg-secondary border-border-subtle',
    icon: <Circle size={12} />
  },
  completed: {
    label: '已完成',
    color: 'text-success-500 bg-success-50 border-success-200',
    icon: <CheckCircle2 size={12} />
  },
  failed: {
    label: '失败',
    color: 'text-error-500 bg-error-50 border-error-200',
    icon: <XCircle size={12} />
  },
  paused: {
    label: '已暂停',
    color: 'text-warning-500 bg-warning-50 border-warning-200',
    icon: <Pause size={12} />
  },
  cancelled: {
    label: '已取消',
    color: 'text-text-tertiary bg-bg-secondary border-border-subtle',
    icon: <XCircle size={12} />
  }
};

const sizeClasses = {
  sm: 'text-xs px-2 py-0.5 gap-1',
  md: 'text-sm px-2.5 py-1 gap-1.5',
  lg: 'text-base px-3 py-1.5 gap-2'
};

export function StatusBadge({ status, size = 'md', showLabel = true, pulse = false }: StatusBadgeProps) {
  const config = statusConfig[status] || statusConfig.pending;

  return (
    <span
      className={[
        'inline-flex items-center rounded-full border font-medium transition-colors',
        config.color,
        sizeClasses[size],
        pulse && status === 'running' ? 'animate-pulse' : ''
      ].join(' ')}
      title={config.label}
    >
      <span className={pulse && status === 'running' ? 'relative' : ''}>
        {config.icon}
        {pulse && status === 'running' && (
          <span className="absolute inset-0 rounded-full animate-ping opacity-30 bg-current" />
        )}
      </span>
      {showLabel && <span>{config.label}</span>}
    </span>
  );
}
