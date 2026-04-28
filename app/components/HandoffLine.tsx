'use client';

import { motion } from 'framer-motion';
import { Agent } from '@/app/types';

interface HandoffLineProps {
  fromAgent: Agent;
  toAgent: Agent;
  isActive: boolean;
}

export default function HandoffLine({ fromAgent, toAgent, isActive }: HandoffLineProps) {
  return (
    <div className="flex items-center gap-3">
      <div
        className="text-xs px-2 py-1 rounded-md border"
        style={{
          color: fromAgent.color,
          borderColor: `${fromAgent.color}40`,
          backgroundColor: `${fromAgent.color}10`,
        }}
      >
        {fromAgent.name}
      </div>

      <div className="flex-1 relative h-0.5 bg-white/5 rounded-full overflow-hidden">
        {isActive && (
          <motion.div
            initial={{ x: '-100%' }}
            animate={{ x: '100%' }}
            transition={{ duration: 1.2, ease: 'easeInOut', repeat: Infinity }}
            className="absolute inset-0 rounded-full"
            style={{
              background: `linear-gradient(90deg, transparent, ${fromAgent.color}, ${toAgent.color}, transparent)`,
            }}
          />
        )}
      </div>

      <div
        className="text-xs px-2 py-1 rounded-md border"
        style={{
          color: toAgent.color,
          borderColor: `${toAgent.color}40`,
          backgroundColor: `${toAgent.color}10`,
        }}
      >
        {toAgent.name}
      </div>
    </div>
  );
}
