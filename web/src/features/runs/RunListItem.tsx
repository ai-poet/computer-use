import { cn } from '../../shared/lib/cn';
import type { Run } from './types';
import { formatRunDate } from './runModel';
import styles from './RunSidebar.module.less';

type Props = {
  run: Run;
  selected: boolean;
  onSelect: (id: string) => void;
};

export function RunListItem({ run, selected, onSelect }: Props) {
  return (
    <button
      className={cn(styles.run, selected && styles.runActive)}
      onClick={() => onSelect(run.id)}
    >
      <div className={styles.runTop}>
        <span className={cn(styles.statusDot, styles[run.status])} />
        <span className={styles.name}>{run.product_name}</span>
        <span className={styles.date}>{formatRunDate(run.started_at)}</span>
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
  );
}
