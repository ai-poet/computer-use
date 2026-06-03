import { cn } from '../../shared/lib/cn';
import type { TerminalLine } from './types';
import { displayText, todoGlyph } from './logModel';
import styles from './LogPanel.module.less';

type Props = {
  line: TerminalLine;
  index: number;
};

function lineClass(line: TerminalLine) {
  return cn(
    styles.line,
    line.indent === 1 && styles.indent1,
    line.indent === 2 && styles.indent2,
    line.kind === 'thinking' && styles.thinking,
    line.tone === 'muted' && styles.muted,
    line.tone === 'accent' && styles.accent,
    line.tone === 'success' && styles.success,
    line.tone === 'warning' && styles.warning,
    line.tone === 'error' && styles.error
  );
}

export function TerminalLineRow({ line, index }: Props) {
  return (
    <span className={lineClass(line)}>
      <span className={styles.lineNo}>{index + 1}</span>
      <span className={styles.content}>
        {line.kind === 'todo' ? (
          <span className={styles.todoText}>
            <span className={styles.todoGlyph}>{todoGlyph(line.status)}</span>
            {line.text}
          </span>
        ) : (
          displayText(line)
        )}
      </span>
    </span>
  );
}
