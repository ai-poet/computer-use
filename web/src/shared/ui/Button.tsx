import type { ButtonHTMLAttributes, ReactNode } from 'react';
import { cn } from '../lib/cn';
import styles from './Button.module.less';

type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger';

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: ButtonVariant;
  iconOnly?: boolean;
  full?: boolean;
  children: ReactNode;
};

export function Button({
  variant = 'secondary',
  iconOnly = false,
  full = false,
  className,
  children,
  ...props
}: ButtonProps) {
  return (
    <button
      className={cn(
        styles.button,
        styles[variant],
        iconOnly && styles.iconOnly,
        full && styles.full,
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
}
