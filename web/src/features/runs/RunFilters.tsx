import { RefreshCw, Search } from 'lucide-react';
import { Button } from '../../shared/ui/Button';
import { cn } from '../../shared/lib/cn';
import type { RunFilterState } from './runModel';
import { RUN_STATUS_FILTERS } from './runModel';
import styles from './RunSidebar.module.less';

type Props = {
  filters: RunFilterState;
  categories: string[];
  onChange: (filters: RunFilterState) => void;
  onRefresh: () => void;
};

export function RunFilters({ filters, categories, onChange, onRefresh }: Props) {
  return (
    <div className={styles.tools}>
      <div className={styles.searchWrap}>
        <Search size={14} className={styles.searchIcon} />
        <input
          className={cn(styles.input, styles.search)}
          value={filters.search}
          onChange={(event) => onChange({ ...filters, search: event.target.value })}
          placeholder="搜索任务..."
        />
      </div>

      <div className={styles.filters}>
        {RUN_STATUS_FILTERS.map((item) => (
          <button
            key={item.key}
            className={cn(styles.chip, filters.status === item.key && styles.chipActive)}
            onClick={() => onChange({ ...filters, status: item.key })}
          >
            {item.label}
          </button>
        ))}
      </div>

      {categories.length > 0 && (
        <div className={styles.filters}>
          <button
            className={cn(styles.chip, filters.category === 'all' && styles.chipActive)}
            onClick={() => onChange({ ...filters, category: 'all' })}
          >
            全部种类
          </button>
          {categories.map((category) => (
            <button
              key={category}
              className={cn(styles.chip, filters.category === category && styles.chipActive)}
              onClick={() => onChange({ ...filters, category })}
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
  );
}
