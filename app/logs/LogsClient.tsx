'use client';

import { motion } from 'framer-motion';
import { LOGS, AGENTS } from '@/app/data/mock';
import { ScrollText, CheckCircle, AlertCircle, AlertTriangle, Info } from 'lucide-react';
import { formatRelativeTime } from '@/app/lib/utils';

const STATUS_CONFIG = {
  success: { color: '#22c55e', icon: CheckCircle },
  error: { color: '#ef4444', icon: AlertCircle },
  warning: { color: '#f59e0b', icon: AlertTriangle },
  info: { color: '#06b6d4', icon: Info },
};

export default function LogsClient() {
  return (
    <div className="min-h-screen p-6 lg:p-8">
      <div className="max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center gap-3 mb-8"
        >
          <ScrollText className="w-5 h-5 text-indigo-400" />
          <div>
            <h1 className="text-xl font-bold text-white/90">Execution Logs</h1>
            <p className="text-sm text-white/35">{LOGS.length} log entries</p>
          </div>
        </motion.div>

        <div className="space-y-2">
          {LOGS.map((log, index) => {
            const statusCfg = STATUS_CONFIG[log.status];
            const StatusIcon = statusCfg.icon;
            const agent = AGENTS.find((a) => a.id === log.agentId);

            return (
              <motion.div
                key={log.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.06 }}
                className="flex items-start gap-3 p-3.5 bg-black/40 backdrop-blur-sm border border-white/5 rounded-xl group hover:border-white/10 transition-colors"
              >
                <StatusIcon
                  className="w-4 h-4 flex-shrink-0 mt-0.5"
                  style={{ color: statusCfg.color }}
                />

                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2 mb-0.5">
                    <div className="flex items-center gap-2">
                      {agent && (
                        <span
                          className="text-xs font-medium"
                          style={{ color: agent.color }}
                        >
                          {log.agentName}
                        </span>
                      )}
                      <span className="text-xs text-white/25 font-mono">{log.action}</span>
                    </div>
                    <span className="text-xs text-white/20 flex-shrink-0">
                      {formatRelativeTime(log.timestamp)}
                    </span>
                  </div>
                  <p className="text-xs text-white/55 leading-relaxed">{log.message}</p>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
