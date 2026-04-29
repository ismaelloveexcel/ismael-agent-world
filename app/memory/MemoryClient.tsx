'use client';

import { motion } from 'framer-motion';
import { MEMORIES, AGENTS } from '@/app/data/mock';
import { Brain, Tag } from 'lucide-react';
import { formatRelativeTime } from '@/app/lib/utils';

export default function MemoryClient() {
  return (
    <div className="min-h-screen p-6 lg:p-8">
      <div className="max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center gap-3 mb-8"
        >
          <Brain className="w-5 h-5 text-indigo-400" />
          <div>
            <h1 className="text-xl font-bold text-white/90">Memory Store</h1>
            <p className="text-sm text-white/35">{MEMORIES.length} indexed fragments</p>
          </div>
        </motion.div>

        <div className="space-y-3">
          {MEMORIES.map((memory, index) => {
            const agent = AGENTS.find((a) => a.id === memory.agentId);
            return (
              <motion.div
                key={memory.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.08 }}
                whileHover={{ x: 4 }}
                className="bg-black/40 backdrop-blur-sm border border-white/10 rounded-xl p-4 group"
              >
                <div className="flex items-start justify-between gap-4">
                  <p className="text-sm text-white/70 leading-relaxed flex-1">{memory.content}</p>
                  <div className="flex flex-col items-end gap-1 flex-shrink-0">
                    <div className="text-xs text-emerald-400 font-medium">
                      {(memory.relevanceScore * 100).toFixed(0)}% relevance
                    </div>
                    <span className="text-xs text-white/25">{formatRelativeTime(memory.createdAt)}</span>
                  </div>
                </div>

                <div className="flex items-center justify-between mt-3">
                  <div className="flex flex-wrap gap-1">
                    {memory.tags.map((tag) => (
                      <span
                        key={tag}
                        className="text-xs px-2 py-0.5 rounded-md bg-cyan-500/10 text-cyan-400/70 border border-cyan-500/20 flex items-center gap-1"
                      >
                        <Tag className="w-2.5 h-2.5" />
                        {tag}
                      </span>
                    ))}
                  </div>
                  {agent && (
                    <span
                      className="text-xs px-2 py-0.5 rounded-md border"
                      style={{
                        color: agent.color,
                        borderColor: `${agent.color}30`,
                        backgroundColor: `${agent.color}10`,
                      }}
                    >
                      {agent.name}
                    </span>
                  )}
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
