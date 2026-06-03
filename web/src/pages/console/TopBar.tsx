import { Moon, RefreshCw, Sun } from 'lucide-react';
import { Button } from '../../shared/ui/Button';
import { StatusBadge } from '../../shared/ui/StatusBadge';
import type { Run } from '../../features/runs/types';
import styles from './TopBar.module.less';

type TopBarProps = {
  run?: Run;
  isDark: boolean;
  onToggleTheme: () => void;
  onRefresh: () => void;
};

export function TopBar({ run, isDark, onToggleTheme, onRefresh }: TopBarProps) {
  return (
    <header className={styles.bar}>
      <div className={styles.identity}>
        <div className={styles.titleRow}>
          <h1 className={styles.title}>{run?.product_name || 'Product Analyzer'}</h1>
          {run && <StatusBadge status={run.status} pulse={run.status === 'running'} />}
        </div>
        <p className={styles.subtitle} title={run?.url}>
          {run?.url || '本地 Linux-first 产品分析控制台'}
        </p>
      </div>
      <div className={styles.actions}>
        <Button iconOnly variant="ghost" onClick={onToggleTheme} title={isDark ? '切换到亮色模式' : '切换到暗色模式'}>
          {isDark ? <Sun size={17} /> : <Moon size={17} />}
        </Button>
        <Button iconOnly variant="ghost" onClick={onRefresh} title="刷新">
          <RefreshCw size={17} />
        </Button>
      </div>
    </header>
  );
}
