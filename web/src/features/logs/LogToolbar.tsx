import { Check, Copy, Download, Terminal } from 'lucide-react';
import { Button } from '../../shared/ui/Button';
import { cn } from '../../shared/lib/cn';
import styles from './LogPanel.module.less';

type Props = {
  connected: boolean;
  autoScroll: boolean;
  copied: boolean;
  onToggleAutoScroll: () => void;
  onCopy: () => void;
  onDownload: () => void;
};

export function LogToolbar({
  connected,
  autoScroll,
  copied,
  onToggleAutoScroll,
  onCopy,
  onDownload
}: Props) {
  return (
    <div className={styles.header}>
      <h2 className={styles.title}>
        <Terminal size={17} />
        实时日志
        <span
          className={cn(styles.connection, connected && styles.connected)}
          title={connected ? '已连接' : '未连接'}
        />
      </h2>
      <div className={styles.actions}>
        <Button variant={autoScroll ? 'secondary' : 'ghost'} onClick={onToggleAutoScroll}>
          {autoScroll ? '自动滚动' : '手动滚动'}
        </Button>
        <Button iconOnly variant="ghost" onClick={onCopy} title="复制日志">
          {copied ? <Check size={16} /> : <Copy size={16} />}
        </Button>
        <Button iconOnly variant="ghost" onClick={onDownload} title="下载日志">
          <Download size={16} />
        </Button>
      </div>
    </div>
  );
}
