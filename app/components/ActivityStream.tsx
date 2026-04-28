'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { ActivityEntry } from '@/app/types';
import { formatRelativeTime } from '@/app/lib/utils';
import { ArrowRight, Brain, BookOpen, ShieldAlert, Check, AlertCircle, Loader2 } from 'lucide-react';

const TYPE_CONFIG: Record<string, { color: string; icon: React.ComponentType<{ className?: string; style?: React.CSSProperties }> }> = {
  handoff: { color: '#6366f1', icon: ArrowRight },
  memory: { color: '#06b6d4', icon: Brain },
  playbook: { color: '#10b981', icon: BookOpen },
  approval: { color: '#f97316', icon: ShieldAlert },
  complete: { color: '#22c55e', icon: Check },
  error: { color: '#ef4444', icon: AlertCircle },
  thinking: { color: '#8b5cf6', icon: Loader2 },
};

interface ActivityStreamProps {
  entries: ActivityEntry[];
}

export default function ActivityStream({ entries }: ActivityStreamProps) {
  return (
    <div className="space-y-2 max-h-80 overflow-y-auto scrollbar-none">
      <AnimatePresence mode="popLayout">
        {entries.map((entry) => {
          const config = TYPE_CONFIG[entry.type] || TYPE_CONFIG.thinking;
          const Icon = config.icon;
          return (
            <motion.div
              key={entry.id}
              initial={{ opacity: 0, x: -20, height: 0 }}
              animate={{ opacity: 1, x: 0, height: 'auto' }}
              exit={{ opacity: 0, x: 20, height: 0 }}
              transition={{ duration: 0.3 }}
              className="flex items-start gap-3 p-3 rounded-lg bg-white/5 border border-white/5"
            >
              <div
                className="w-6 h-6 rounded-md flex items-center justify-center flex-shrink-0 mt-0.5"
                style={{ backgroundColor: `${config.color}20` }}
              >
                <Icon className="w-3 h-3" style={{ color: config.color }} />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-xs font-medium text-white/70 truncate">
                    {entry.agentName}
                  </span>
                  <span className="text-xs text-white/25 flex-shrink-0">
                    {formatRelativeTime(entry.timestamp)}
                  </span>
                </div>
                <p className="text-xs text-white/45 mt-0.5 leading-relaxed">{entry.message}</p>
              </div>
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
}
