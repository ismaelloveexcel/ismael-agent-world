'use client';

import * as React from 'react';
import { motion, type HTMLMotionProps } from 'framer-motion';
import { cn } from '@/lib/utils';

// ─── Variant Maps ─────────────────────────────────────────────────────────────

const variantClasses: Record<ButtonVariant, string> = {
  primary:
    'bg-teal-500 text-slate-950 hover:bg-teal-400 shadow-[0_0_12px_#0abf9f40] hover:shadow-[0_0_20px_#0abf9f80]',
  secondary:
    'bg-transparent border border-teal-500 text-teal-500 hover:bg-teal-500/10',
  ghost:
    'bg-transparent text-slate-400 hover:text-slate-100 hover:bg-slate-800',
  destructive:
    'bg-red-600/20 border border-red-500 text-red-400 hover:bg-red-600/30',
  blue:
    'bg-blue-500 text-white hover:bg-blue-400 shadow-[0_0_12px_#3b82f640] hover:shadow-[0_0_20px_#3b82f680]',
};

const sizeClasses: Record<ButtonSize, string> = {
  sm:   'h-8  px-3  text-xs  gap-1.5',
  md:   'h-9  px-4  text-sm  gap-2',
  lg:   'h-11 px-6  text-base gap-2.5',
  icon: 'h-9  w-9  text-sm',
};

// ─── Types ────────────────────────────────────────────────────────────────────

type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'destructive' | 'blue';
type ButtonSize    = 'sm' | 'md' | 'lg' | 'icon';

export interface ButtonProps
  extends Omit<HTMLMotionProps<'button'>, 'children'> {
  variant?:  ButtonVariant;
  size?:     ButtonSize;
  loading?:  boolean;
  children?: React.ReactNode;
}

// ─── Motion Variants ─────────────────────────────────────────────────────────

const tapVariant = { scale: 0.97 } as const;
const hoverVariant = { scale: 1.02 } as const;

// ─── Component ───────────────────────────────────────────────────────────────

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant  = 'primary',
      size     = 'md',
      loading  = false,
      disabled,
      className,
      children,
      ...props
    },
    ref
  ) => {
    const isDisabled = disabled || loading;

    return (
      <motion.button
        ref={ref}
        whileHover={isDisabled ? undefined : hoverVariant}
        whileTap={isDisabled ? undefined : tapVariant}
        transition={{ type: 'spring', stiffness: 400, damping: 25 }}
        disabled={isDisabled}
        className={cn(
          // Base
          'inline-flex items-center justify-center font-medium rounded-md',
          'transition-colors duration-150 cursor-pointer',
          'focus-visible:outline-none focus-visible:ring-2',
          'focus-visible:ring-teal-500 focus-visible:ring-offset-2',
          'focus-visible:ring-offset-slate-950',
          // Disabled
          'disabled:opacity-40 disabled:cursor-not-allowed disabled:pointer-events-none',
          // Variant + Size
          variantClasses[variant],
          sizeClasses[size],
          className
        )}
        aria-busy={loading}
        {...props}
      >
        {loading ? (
          <span className="flex items-center gap-2">
            <LoadingSpinner />
            {children}
          </span>
        ) : (
          children
        )}
      </motion.button>
    );
  }
);

Button.displayName = 'Button';

// ─── Internal Spinner ─────────────────────────────────────────────────────────

function LoadingSpinner(): React.JSX.Element {
  return (
    <motion.span
      className="block h-3.5 w-3.5 rounded-full border-2 border-current border-t-transparent"
      animate={{ rotate: 360 }}
      transition={{ duration: 0.7, repeat: Infinity, ease: 'linear' }}
      aria-hidden="true"
    />
  );
}
