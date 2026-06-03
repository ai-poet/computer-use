import type { RefObject } from 'react';
import { Terminal } from 'lucide-react';
import { EmptyState } from '../../shared/ui/EmptyState';
import type { Run } from '../runs/types';
import type { TerminalLine } from './types';
import { TerminalLineRow } from './TerminalLineRow';
import styles from './LogPanel.module.less';

type Props = {
  lines: TerminalLine[];
  run?: Run;
  scrollRef: RefObject<HTMLPreElement | null>;
  onScroll: () => void;
};

export function TerminalViewport({ lines, run, scrollRef, onScroll }: Props) {
  return (
    <pre className={styles.terminal} ref={scrollRef} onScroll={onScroll}>
      {lines.length === 0 ? (
        <span className={styles.emptyWrap}>
          <EmptyState
            title={run?.status === 'completed' ? '任务已完成' : '等待事件...'}
            description={run ? '日志流连接后会显示 Codex 终端事件' : '请选择一个任务'}
            icon={Terminal}
          />
        </span>
      ) : (
        lines.map((line, index) => (
          <TerminalLineRow key={line.id || index} line={line} index={index} />
        ))
      )}
    </pre>
  );
}
