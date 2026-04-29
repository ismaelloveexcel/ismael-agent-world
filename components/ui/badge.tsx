'use client';

import * as React from 'react';
import { motion, type HTMLMotionProps } from 'framer-motion';
import { cn } from '@/lib/utils';

// ─── Types ────────────────────────────────────────────────────────────────────

type BadgeVariant =
  | 'default'
  | 'teal'
  | 'blue'
  | 'amber'
  | 'red'
  | 'green'
  | 'outline'
  | 'agent-idle'
  | 'agent-thinking'
  | 'agent-active'
  | 'agent-error'
  | 'agent-success';

export interface BadgeProps extends Omit<HTMLMotionProps<'span'>, 'children'> {
  variant?: BadgeVariant;
  dot?:     boolean;
  pulse?:   boolean;
  children?: React.ReactNode;
}

// ─── Variant Maps ─────────────────────────────────────────────────────────────

const variantClasses: Record<BadgeVariant, string> = {
  default:         'bg-slate-800 text-slate-300 border border-slate-700',
  teal:            'bg-teal-500/15 text-teal-400 border border-teal-500/30',
  blue:            'bg-blue-500/15 text-blue-400 border border-blue-500/30',
  amber:           'bg-amber-500/15 text-amber-400 border border-amber-500/30',
  red:             'bg-red-500/15 text-red-400 border border-red-500/30',
  green:           'bg-green-500/15 text-green-400 border border-green-500/30',
  outline:         'bg-transparent text-slate-400 border border-slate-600',
  'agent-idle':    'bg-slate-700/40 text-slate-400 border border-slate-600',
  'agent-thinking':'bg-amber-500/10 text-amber-400 border border-amber-500/25',
  'agent-active':  'bg-teal-500/10 text-teal-400 border border-teal-500/25',
  'agent-error':   'bg-red-500/10 text-red-400 border border-red-500/25',
  'agent-success': 'bg-green-500/10 text-green-400 border border-green-500/25',
};

const dotColors: Record<BadgeVariant, string> = {
  default:          'bg-slate-400',
  teal:             'bg-teal-400',
  blue:             'bg-blue-400',
  amber:            'bg-amber-400',
  red:              'bg-red-400',
  green:            'bg-green-400',
  outline:          'bg-slate-400',
  'agent-idle':     'bg-slate-500',
  'agent-thinking': 'bg-amber-400',
  'agent-active':   'bg-teal-400',
  'agent-error':    'bg-red-400',
  'agent-success':  'bg-green-400',
};

// ─── Component ───────────────────────────────────────────────────────────────

export function Badge({
  variant = 'default',
  dot     = false,
  pulse   = false,
  className,
  children,
  ...props
}: BadgeProps): React.JSX.Element {
  return (
    <motion.span
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.15, ease: 'easeOut' }}
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5',
        'text-xs font-medium leading-none whitespace-nowrap',
        variantClasses[variant],
        className
      )}
      {...props}
    >
      {dot && (
        <span className="relative flex h-1.5 w-1.5 flex-shrink-0">
          {pulse && (
            <span
              className={cn(
                'absolute inline-flex h-full w-full rounded-full opacity-75 animate-ping',
                dotColors[variant]
              )}
            />
          )}
          <span
            className={cn(
              'relative inline-flex rounded-full h-1.5 w-1.5',
              dotColors[variant]
            )}
          />
        </span>
      )}
      {children}
    </motion.span>
  );
}
