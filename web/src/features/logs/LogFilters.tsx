import { cn } from '../../shared/lib/cn';
import { LOG_FILTERS } from './logModel';
import type { LogFilterKey } from './logModel';
import styles from './LogPanel.module.less';

type Props = {
  value: LogFilterKey;
  onChange: (filter: LogFilterKey) => void;
};

export function LogFilters({ value, onChange }: Props) {
  return (
    <div className={styles.filters}>
      {LOG_FILTERS.map((item) => (
        <button
          key={item.key}
          className={cn(styles.chip, value === item.key && styles.chipActive)}
          onClick={() => onChange(item.key)}
        >
          {item.label}
        </button>
      ))}
    </div>
  );
}
