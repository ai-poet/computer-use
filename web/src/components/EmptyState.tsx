import { Inbox, SearchX, AlertTriangle, Loader2, Plus } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

interface EmptyStateProps {
  variant?: 'empty' | 'search' | 'error' | 'loading';
  title: string;
  description?: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  icon?: LucideIcon;
}

const variantConfig = {
  empty: { icon: Inbox, color: 'text-text-tertiary' },
  search: { icon: SearchX, color: 'text-text-tertiary' },
  error: { icon: AlertTriangle, color: 'text-error-500' },
  loading: { icon: Loader2, color: 'text-primary-500' }
};

export function EmptyState({
  variant = 'empty',
  title,
  description,
  action,
  icon: CustomIcon
}: EmptyStateProps) {
  const config = variantConfig[variant];
  const Icon = CustomIcon || config.icon;

  return (
    <div className="flex flex-col items-center justify-center py-12 px-4 text-center animate-fade-in-up">
      <div className={`mb-4 ${variant === 'loading' ? 'animate-spin' : ''}`}>
        <Icon size={48} className={config.color} strokeWidth={1.5} />
      </div>
      <h3 className="text-lg font-semibold text-text-primary mb-1">{title}</h3>
      {description && (
        <p className="text-sm text-text-secondary max-w-xs mb-4">{description}</p>
      )}
      {action && (
        <button
          onClick={action.onClick}
          className="inline-flex items-center gap-2 px-4 py-2 bg-primary-500 text-white rounded-md text-sm font-medium hover:bg-primary-600 transition-colors"
        >
          <Plus size={16} />
          {action.label}
        </button>
      )}
    </div>
  );
}
