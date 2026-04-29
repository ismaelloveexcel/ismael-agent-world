'use client';

import { motion } from 'framer-motion';
import { Agent } from '@/app/types';
import { getStateColor, getStateLabel } from '@/app/lib/utils';
import {
  Crown, GitBranch, Database, BookOpen, Zap, Hammer,
  ShieldCheck, Brain, Lock
} from 'lucide-react';

const ICON_MAP: Record<string, React.ComponentType<{ className?: string; style?: React.CSSProperties }>> = {
  Crown, GitBranch, Database, BookOpen, Zap, Hammer, ShieldCheck, Brain, Lock,
};

interface AgentCardProps {
  agent: Agent;
  index?: number;
}

export default function AgentCard({ agent, index = 0 }: AgentCardProps) {
  const Icon = ICON_MAP[agent.icon] || Zap;
  const stateColor = getStateColor(agent.state);
  const stateLabel = getStateLabel(agent.state);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.08, duration: 0.5 }}
      whileHover={{ y: -4, scale: 1.01 }}
      className="relative bg-black/40 backdrop-blur-sm border border-white/10 rounded-2xl p-5 overflow-hidden group cursor-pointer"
    >
      <div
        className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 rounded-2xl"
        style={{
          background: `radial-gradient(circle at 50% 0%, ${agent.color}15 0%, transparent 70%)`,
        }}
      />

      <div className="relative z-10">
        <div className="flex items-start justify-between mb-4">
          <div
            className="w-10 h-10 rounded-xl flex items-center justify-center"
            style={{ backgroundColor: `${agent.color}20`, border: `1px solid ${agent.color}40` }}
          >
            <Icon className="w-5 h-5" style={{ color: agent.color }} />
          </div>
          <div className="flex items-center gap-1.5">
            <motion.div
              animate={
                agent.state !== 'idle' && agent.state !== 'completed'
                  ? { scale: [1, 1.3, 1], opacity: [0.8, 1, 0.8] }
                  : {}
              }
              transition={{ duration: 1.5, repeat: Infinity }}
              className="w-2 h-2 rounded-full"
              style={{ backgroundColor: stateColor }}
            />
            <span className="text-xs" style={{ color: stateColor }}>
              {stateLabel}
            </span>
          </div>
        </div>

        <h3 className="text-sm font-semibold text-white mb-0.5">{agent.name}</h3>
        <p className="text-xs text-white/40 mb-3">{agent.role}</p>
        <p className="text-xs text-white/50 leading-relaxed mb-4">{agent.description}</p>

        <div className="flex flex-wrap gap-1">
          {agent.capabilities.slice(0, 3).map((cap) => (
            <span
              key={cap}
              className="text-xs px-2 py-0.5 rounded-md bg-white/5 text-white/40 border border-white/5"
            >
              {cap.replace(/_/g, ' ')}
            </span>
          ))}
        </div>
      </div>

      <div
        className="absolute bottom-0 left-0 right-0 h-px opacity-0 group-hover:opacity-100 transition-opacity duration-500"
        style={{ background: `linear-gradient(90deg, transparent, ${agent.color}60, transparent)` }}
      />
    </motion.div>
  );
}
