'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { APPROVALS } from '@/app/data/mock';
import { Approval } from '@/app/types';
import { ShieldAlert, Check, X, ChevronDown, AlertTriangle } from 'lucide-react';
import { formatRelativeTime } from '@/app/lib/utils';

const RISK_CONFIG = {
  low: { color: '#22c55e', label: 'Low Risk' },
  medium: { color: '#f59e0b', label: 'Medium Risk' },
  high: { color: '#ef4444', label: 'High Risk' },
  critical: { color: '#dc2626', label: 'Critical' },
};

export default function ApprovalsClient() {
  const [approvals, setApprovals] = useState<Approval[]>(APPROVALS);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const handleAction = (id: string, action: 'approved' | 'rejected') => {
    setApprovals((prev) =>
      prev.map((a) =>
        a.id === id
          ? { ...a, status: action, resolvedAt: new Date().toISOString() }
          : a
      )
    );
  };

  const pending = approvals.filter((a) => a.status === 'pending');
  const resolved = approvals.filter((a) => a.status !== 'pending');

  return (
    <div className="min-h-screen p-6 lg:p-8">
      <div className="max-w-3xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center gap-3 mb-8"
        >
          <ShieldAlert className="w-5 h-5 text-orange-400" />
          <div>
            <h1 className="text-xl font-bold text-white/90">Approvals</h1>
            <p className="text-sm text-white/35">
              {pending.length} pending · {resolved.length} resolved
            </p>
          </div>
          {pending.length > 0 && (
            <div className="ml-auto flex items-center gap-1.5 text-xs text-orange-400 bg-orange-400/10 border border-orange-400/20 px-2.5 py-1 rounded-full">
              <AlertTriangle className="w-3 h-3" />
              {pending.length} awaiting review
            </div>
          )}
        </motion.div>

        <div className="space-y-3">
          <AnimatePresence>
            {approvals.map((approval, index) => {
              const riskCfg = RISK_CONFIG[approval.riskLevel];
              const isExpanded = expandedId === approval.id;
              const isPending = approval.status === 'pending';

              return (
                <motion.div
                  key={approval.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.08 }}
                  className="bg-black/40 backdrop-blur-sm border rounded-xl overflow-hidden"
                  style={{
                    borderColor: isPending ? `${riskCfg.color}30` : 'rgba(255,255,255,0.05)',
                  }}
                >
                  <div
                    className="p-4 cursor-pointer"
                    onClick={() => setExpandedId(isExpanded ? null : approval.id)}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span
                            className="text-xs px-2 py-0.5 rounded-md border"
                            style={{
                              color: riskCfg.color,
                              borderColor: `${riskCfg.color}40`,
                              backgroundColor: `${riskCfg.color}10`,
                            }}
                          >
                            {riskCfg.label}
                          </span>
                          <span className="text-xs text-white/30">
                            {approval.requestedBy}
                          </span>
                        </div>
                        <p className="text-sm text-white/70">{approval.reason}</p>
                      </div>

                      <div className="flex items-center gap-2 flex-shrink-0">
                        <span className="text-xs text-white/25">
                          {formatRelativeTime(approval.createdAt)}
                        </span>
                        {!isPending && (
                          <span
                            className={`text-xs px-2 py-0.5 rounded-md ${
                              approval.status === 'approved'
                                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                                : 'bg-red-500/10 text-red-400 border border-red-500/20'
                            }`}
                          >
                            {approval.status}
                          </span>
                        )}
                        <ChevronDown
                          className={`w-4 h-4 text-white/30 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                        />
                      </div>
                    </div>
                  </div>

                  <AnimatePresence>
                    {isExpanded && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.2 }}
                        className="overflow-hidden"
                      >
                        <div className="px-4 pb-4 border-t border-white/5 pt-3">
                          <p className="text-xs text-white/40 mb-2">Payload</p>
                          <pre className="text-xs text-white/50 bg-white/5 rounded-lg p-3 overflow-auto scrollbar-none">
                            {JSON.stringify(approval.payload, null, 2)}
                          </pre>

                          {isPending && (
                            <div className="flex gap-2 mt-3">
                              <button
                                onClick={() => handleAction(approval.id, 'approved')}
                                className="flex-1 flex items-center justify-center gap-2 py-2 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-sm hover:bg-emerald-500/20 transition-colors"
                              >
                                <Check className="w-4 h-4" />
                                Approve
                              </button>
                              <button
                                onClick={() => handleAction(approval.id, 'rejected')}
                                className="flex-1 flex items-center justify-center gap-2 py-2 rounded-lg bg-red-500/10 text-red-400 border border-red-500/20 text-sm hover:bg-red-500/20 transition-colors"
                              >
                                <X className="w-4 h-4" />
                                Reject
                              </button>
                            </div>
                          )}
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </motion.div>
              );
            })}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
