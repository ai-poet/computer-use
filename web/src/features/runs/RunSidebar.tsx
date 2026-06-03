import { useEffect, useMemo, useState } from 'react';
import { ShieldCheck } from 'lucide-react';
import type { CreateRunPayload, Run } from './types';
import { RunCreateForm } from './RunCreateForm';
import { RunFilters } from './RunFilters';
import { RunList } from './RunList';
import {
  collectRunCategories,
  DEFAULT_RUN_FILTERS,
  filterRuns
} from './runModel';
import type { RunFilterState } from './runModel';
import styles from './RunSidebar.module.less';

type Props = {
  runs: Run[];
  selected: string;
  onSelect: (id: string) => void;
  onRefresh: () => void;
  onCreate: (payload: CreateRunPayload) => Promise<unknown>;
  isLoading?: boolean;
};

export function RunSidebar({ runs, selected, onSelect, onRefresh, onCreate, isLoading }: Props) {
  const [filters, setFilters] = useState<RunFilterState>(DEFAULT_RUN_FILTERS);

  const categories = useMemo(() => collectRunCategories(runs), [runs]);
  const filteredRuns = useMemo(() => filterRuns(runs, filters), [runs, filters]);

  useEffect(() => {
    if (filters.category !== 'all' && !categories.includes(filters.category)) {
      setFilters((current) => ({ ...current, category: 'all' }));
    }
  }, [categories, filters.category]);

  return (
    <aside className={styles.sidebar}>
      <div className={styles.brand}>
        <ShieldCheck size={22} />
        Analyzer
        <span className={styles.version}>v1.0</span>
      </div>

      <RunCreateForm onCreate={onCreate} />
      <RunFilters filters={filters} categories={categories} onChange={setFilters} onRefresh={onRefresh} />
      <RunList runs={filteredRuns} selected={selected} isLoading={isLoading} onSelect={onSelect} />
    </aside>
  );
}
