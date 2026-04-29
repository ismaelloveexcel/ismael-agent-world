'use client';

import * as React from 'react';
import { motion, type HTMLMotionProps } from 'framer-motion';
import { cn } from '@/lib/utils';

// ─── Types ────────────────────────────────────────────────────────────────────

type CardVariant = 'default' | 'elevated' | 'outlined' | 'agent';

export interface CardProps extends HTMLMotionProps<'div'> {
  variant?:   CardVariant;
  hoverable?: boolean;
}

// ─── Variant Maps ─────────────────────────────────────────────────────────────

const variantClasses: Record<CardVariant, string> = {
  default:
    'bg-slate-900 border border-slate-800',
  elevated:
    'bg-slate-800 border border-slate-700 shadow-xl shadow-black/40',
  outlined:
    'bg-transparent border border-teal-500/30',
  agent:
    'bg-slate-900 border border-slate-800 shadow-[inset_0_1px_0_rgba(255,255,255,0.04)]',
};

const hoverClasses: Record<CardVariant, string> = {
  default:  'hover:border-slate-700 hover:bg-slate-900/80',
  elevated: 'hover:border-slate-600 hover:shadow-2xl',
  outlined: 'hover:border-teal-500/60 hover:shadow-[0_0_16px_#0abf9f20]',
  agent:    'hover:border-teal-500/40 hover:shadow-[0_0_12px_#0abf9f15]',
};

// ─── Card Root ────────────────────────────────────────────────────────────────

export const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ variant = 'default', hoverable = false, className, children, ...props }, ref) => (
    <motion.div
      ref={ref}
      className={cn(
        'rounded-lg transition-all duration-200',
        variantClasses[variant],
        hoverable && hoverClasses[variant],
        hoverable && 'cursor-pointer',
        className
      )}
      {...props}
    >
      {children}
    </motion.div>
  )
);

Card.displayName = 'Card';

// ─── Card Header ─────────────────────────────────────────────────────────────

export interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

export function CardHeader({ className, children, ...props }: CardHeaderProps): React.JSX.Element {
  return (
    <div
      className={cn('flex flex-col gap-1.5 p-5 pb-0', className)}
      {...props}
    >
      {children}
    </div>
  );
}

// ─── Card Title ───────────────────────────────────────────────────────────────

export interface CardTitleProps extends React.HTMLAttributes<HTMLHeadingElement> {
  children: React.ReactNode;
}

export function CardTitle({ className, children, ...props }: CardTitleProps): React.JSX.Element {
  return (
    <h3
      className={cn('text-sm font-semibold text-slate-100 leading-tight', className)}
      {...props}
    >
      {children}
    </h3>
  );
}

// ─── Card Description ─────────────────────────────────────────────────────────

export interface CardDescriptionProps extends React.HTMLAttributes<HTMLParagraphElement> {
  children: React.ReactNode;
}

export function CardDescription({ className, children, ...props }: CardDescriptionProps): React.JSX.Element {
  return (
    <p
      className={cn('text-xs text-slate-400 leading-relaxed', className)}
      {...props}
    >
      {children}
    </p>
  );
}

// ─── Card Content ─────────────────────────────────────────────────────────────

export interface CardContentProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

export function CardContent({ className, children, ...props }: CardContentProps): React.JSX.Element {
  return (
    <div
      className={cn('p-5', className)}
      {...props}
    >
      {children}
    </div>
  );
}

// ─── Card Footer ──────────────────────────────────────────────────────────────

export interface CardFooterProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

export function CardFooter({ className, children, ...props }: CardFooterProps): React.JSX.Element {
  return (
    <div
      className={cn(
        'flex items-center px-5 pb-5 pt-0 gap-3 border-t border-slate-800/60 mt-4 pt-4',
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}
