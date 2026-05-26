import { Loader2 } from 'lucide-react';

interface LoadingStateProps {
  variant?: 'skeleton' | 'spinner' | 'progress' | 'skeleton-text' | 'skeleton-card';
  count?: number;
  progress?: number;
  className?: string;
}

export function LoadingState({
  variant = 'spinner',
  count = 3,
  progress = 0,
  className = ''
}: LoadingStateProps) {
  if (variant === 'spinner') {
    return (
      <div className={`flex items-center justify-center py-8 ${className}`}>
        <Loader2 size={24} className="animate-spin text-primary-500" />
      </div>
    );
  }

  if (variant === 'progress') {
    return (
      <div className={`w-full py-4 ${className}`}>
        <div className="w-full h-2 bg-bg-tertiary rounded-full overflow-hidden">
          <div
            className="h-full bg-primary-500 rounded-full transition-all duration-300"
            style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
          />
        </div>
        <p className="text-xs text-text-tertiary mt-2 text-center">{progress}%</p>
      </div>
    );
  }

  if (variant === 'skeleton-text') {
    return (
      <div className={`space-y-3 py-4 ${className}`}>
        {Array.from({ length: count }).map((_, i) => (
          <div
            key={i}
            className="h-4 bg-bg-tertiary rounded animate-skeleton"
            style={{ width: `${70 + Math.random() * 30}%` }}
          />
        ))}
      </div>
    );
  }

  if (variant === 'skeleton-card') {
    return (
      <div className={`space-y-4 py-4 ${className}`}>
        {Array.from({ length: count }).map((_, i) => (
          <div
            key={i}
            className="p-4 border border-border-subtle rounded-lg bg-surface"
          >
            <div className="h-5 w-1/3 bg-bg-tertiary rounded mb-3 animate-skeleton" />
            <div className="h-4 w-2/3 bg-bg-tertiary rounded mb-2 animate-skeleton" />
            <div className="h-4 w-1/2 bg-bg-tertiary rounded animate-skeleton" />
          </div>
        ))}
      </div>
    );
  }

  // Default skeleton
  return (
    <div className={`space-y-4 py-4 ${className}`}>
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-bg-tertiary animate-skeleton flex-shrink-0" />
          <div className="flex-1 space-y-2">
            <div className="h-4 w-3/4 bg-bg-tertiary rounded animate-skeleton" />
            <div className="h-3 w-1/2 bg-bg-tertiary rounded animate-skeleton" />
          </div>
        </div>
      ))}
    </div>
  );
}
