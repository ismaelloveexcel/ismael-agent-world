'use client';

import { motion } from 'framer-motion';
import { PROJECTS, PLAYBOOKS } from '@/app/data/mock';
import { FolderOpen, Clock, CheckCircle, PauseCircle, XCircle } from 'lucide-react';

const STATUS_CONFIG = {
  active: { color: '#22c55e', icon: Clock, label: 'Active' },
  paused: { color: '#f59e0b', icon: PauseCircle, label: 'Paused' },
  completed: { color: '#6366f1', icon: CheckCircle, label: 'Completed' },
  failed: { color: '#ef4444', icon: XCircle, label: 'Failed' },
};

export default function ProjectsClient() {
  return (
    <div className="min-h-screen p-6 lg:p-8">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center gap-3 mb-8"
        >
          <FolderOpen className="w-5 h-5 text-indigo-400" />
          <div>
            <h1 className="text-xl font-bold text-white/90">Projects</h1>
            <p className="text-sm text-white/35">{PROJECTS.length} projects tracked</p>
          </div>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {PROJECTS.map((project, index) => {
            const statusCfg = STATUS_CONFIG[project.status];
            const StatusIcon = statusCfg.icon;
            const playbook = PLAYBOOKS.find((p) => p.id === project.playbookId);

            return (
              <motion.div
                key={project.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ y: -3 }}
                className="bg-black/40 backdrop-blur-sm border border-white/10 rounded-2xl p-5 overflow-hidden group"
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="text-sm font-semibold text-white/90">{project.name}</h3>
                    <p className="text-xs text-white/40 mt-0.5">{project.description}</p>
                  </div>
                  <div
                    className="flex items-center gap-1.5 text-xs px-2 py-1 rounded-md border flex-shrink-0 ml-2"
                    style={{
                      color: statusCfg.color,
                      borderColor: `${statusCfg.color}40`,
                      backgroundColor: `${statusCfg.color}10`,
                    }}
                  >
                    <StatusIcon className="w-3 h-3" />
                    {statusCfg.label}
                  </div>
                </div>

                <div className="mb-3">
                  <div className="flex justify-between text-xs text-white/40 mb-1">
                    <span>Progress</span>
                    <span>{project.progress}%</span>
                  </div>
                  <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${project.progress}%` }}
                      transition={{ delay: index * 0.1 + 0.3, duration: 1, ease: 'easeOut' }}
                      className="h-full rounded-full"
                      style={{ backgroundColor: statusCfg.color }}
                    />
                  </div>
                </div>

                {playbook && (
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-xs text-white/30">Playbook:</span>
                    <span className="text-xs text-indigo-400">{playbook.name}</span>
                  </div>
                )}

                <div className="flex flex-wrap gap-1">
                  {project.tags.map((tag) => (
                    <span
                      key={tag}
                      className="text-xs px-2 py-0.5 rounded-md bg-white/5 text-white/35 border border-white/5"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
