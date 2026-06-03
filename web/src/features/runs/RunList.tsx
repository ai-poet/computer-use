import { EmptyState } from '../../shared/ui/EmptyState';
import type { Run } from './types';
import { RunListItem } from './RunListItem';
import styles from './RunSidebar.module.less';

type Props = {
  runs: Run[];
  selected: string;
  isLoading?: boolean;
  onSelect: (id: string) => void;
};

export function RunList({ runs, selected, isLoading, onSelect }: Props) {
  if (isLoading) {
    return (
      <div className={styles.list}>
        <div className={styles.loading}>
          <div className={styles.skeleton} />
          <div className={styles.skeleton} />
          <div className={styles.skeleton} />
        </div>
      </div>
    );
  }

  if (runs.length === 0) {
    return (
      <div className={styles.list}>
        <EmptyState title="暂无任务" description="创建一次分析后，这里会显示任务进度" />
      </div>
    );
  }

  return (
    <div className={styles.list}>
      {runs.map((run) => (
        <RunListItem
          key={run.id}
          run={run}
          selected={run.id === selected}
          onSelect={onSelect}
        />
      ))}
    </div>
  );
}
