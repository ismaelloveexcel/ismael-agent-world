'use client';

import { motion } from 'framer-motion';
import { PLAYBOOKS } from '@/app/data/mock';
import { BookOpen, ChevronRight } from 'lucide-react';

const DOMAIN_COLORS: Record<string, string> = {
  Engineering: '#6366f1',
  Operations: '#10b981',
  Analytics: '#06b6d4',
  Research: '#8b5cf6',
  Strategy: '#f59e0b',
  Marketing: '#ec4899',
};

export default function PlaybooksClient() {
  return (
    <div className="min-h-screen p-6 lg:p-8">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center gap-3 mb-8"
        >
          <BookOpen className="w-5 h-5 text-indigo-400" />
          <div>
            <h1 className="text-xl font-bold text-white/90">Playbooks</h1>
            <p className="text-sm text-white/35">{PLAYBOOKS.length} workflow templates</p>
          </div>
        </motion.div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {PLAYBOOKS.map((playbook, index) => {
            const domainColor = DOMAIN_COLORS[playbook.domain] || '#6366f1';
            return (
              <motion.div
                key={playbook.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.06 }}
                whileHover={{ y: -4 }}
                className="bg-black/40 backdrop-blur-sm border border-white/10 rounded-2xl p-5 group cursor-pointer relative overflow-hidden"
              >
                <div
                  className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 rounded-2xl"
                  style={{
                    background: `radial-gradient(circle at 100% 0%, ${domainColor}10 0%, transparent 60%)`,
                  }}
                />

                <div className="relative z-10">
                  <div className="flex items-start justify-between mb-3">
                    <h3 className="text-sm font-semibold text-white/90">{playbook.name}</h3>
                    <span
                      className="text-xs px-2 py-0.5 rounded-md border flex-shrink-0 ml-2"
                      style={{
                        color: domainColor,
                        borderColor: `${domainColor}40`,
                        backgroundColor: `${domainColor}10`,
                      }}
                    >
                      {playbook.domain}
                    </span>
                  </div>

                  <p className="text-xs text-white/45 leading-relaxed mb-4">{playbook.description}</p>

                  <div className="space-y-1.5 mb-4">
                    {playbook.steps.slice(0, 3).map((step) => (
                      <div key={step.id} className="flex items-center gap-2">
                        <div className="w-4 h-4 rounded-full border border-white/10 flex items-center justify-center flex-shrink-0">
                          <span className="text-white/30" style={{ fontSize: '9px' }}>{step.order}</span>
                        </div>
                        <span className="text-xs text-white/35">{step.description}</span>
                        {step.requiresApproval && (
                          <span className="text-xs text-orange-400/60 ml-auto">⚠</span>
                        )}
                      </div>
                    ))}
                    {playbook.steps.length > 3 && (
                      <span className="text-xs text-white/25 ml-6">+{playbook.steps.length - 3} more steps</span>
                    )}
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-xs text-white/25">{playbook.usageCount} runs</span>
                    <ChevronRight className="w-3.5 h-3.5 text-white/20 group-hover:text-white/50 transition-colors" />
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
