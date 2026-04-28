'use client';

import { motion } from 'framer-motion';
import AgentCard from '@/app/components/AgentCard';
import { AGENTS } from '@/app/data/mock';
import { Users } from 'lucide-react';

export default function AgentsClient() {
  return (
    <div className="min-h-screen p-6 lg:p-8">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center gap-3 mb-8"
        >
          <Users className="w-5 h-5 text-indigo-400" />
          <div>
            <h1 className="text-xl font-bold text-white/90">Agent Registry</h1>
            <p className="text-sm text-white/35">{AGENTS.length} core agents active</p>
          </div>
        </motion.div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {AGENTS.map((agent, index) => (
            <AgentCard key={agent.id} agent={agent} index={index} />
          ))}
        </div>
      </div>
    </div>
  );
}
