import { cn } from '../lib/cn';
import type { RunStatus } from '../../features/runs/types';
import styles from './StatusBadge.module.less';

const labels: Record<RunStatus, string> = {
  running: '运行中',
  pending: '等待中',
  completed: '已完成',
  failed: '失败',
  paused: '已暂停',
  cancelled: '已取消'
};

export function StatusBadge({ status, pulse = false }: { status: RunStatus; pulse?: boolean }) {
  return (
    <span className={cn(styles.badge, styles[status], pulse && styles.pulse)}>
      <span className={styles.dot} />
      {labels[status] || status}
    </span>
  );
}
