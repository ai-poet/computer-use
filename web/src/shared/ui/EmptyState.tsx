import type { LucideIcon } from 'lucide-react';
import { Inbox } from 'lucide-react';
import styles from './EmptyState.module.less';

type EmptyStateProps = {
  title: string;
  description?: string;
  icon?: LucideIcon;
};

export function EmptyState({ title, description, icon: Icon = Inbox }: EmptyStateProps) {
  return (
    <div className={styles.empty}>
      <Icon size={28} className={styles.icon} />
      <p className={styles.title}>{title}</p>
      {description && <p className={styles.description}>{description}</p>}
    </div>
  );
}
