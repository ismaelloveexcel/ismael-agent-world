'use client';

import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import CommandOrb from '@/app/components/CommandOrb';
import ActivityStream from '@/app/components/ActivityStream';
import HandoffLine from '@/app/components/HandoffLine';
import { AGENTS } from '@/app/data/mock';
import { ActivityEntry, Agent } from '@/app/types';
import { getStateColor } from '@/app/lib/utils';
import { Sparkles, Activity } from 'lucide-react';

const RISKY_KEYWORDS = ['deploy', 'delete', 'write', 'push', 'publish', 'send', 'execute', 'run script'];

function generateId() {
  return Math.random().toString(36).substr(2, 9);
}

export default function CommandPage() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [activeAgents, setActiveAgents] = useState<Agent[]>([]);
  const [activity, setActivity] = useState<ActivityEntry[]>([]);
  const [currentHandoff, setCurrentHandoff] = useState<{ from: Agent; to: Agent } | null>(null);

  const addActivity = useCallback((entry: Omit<ActivityEntry, 'id' | 'timestamp'>) => {
    setActivity((prev) => [
      {
        ...entry,
        id: generateId(),
        timestamp: new Date().toISOString(),
      },
      ...prev.slice(0, 49),
    ]);
  }, []);

  const setAgentState = useCallback((agentId: string, state: Agent['state']) => {
    setActiveAgents((prev) =>
      prev.map((a) => (a.id === agentId ? { ...a, state } : a))
    );
  }, []);

  const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

  const runPipeline = useCallback(async (command: string) => {
    const isRisky = RISKY_KEYWORDS.some((kw) => command.toLowerCase().includes(kw));
    const chiefAgent = AGENTS.find((a) => a.id === 'chief-agent')!;
    const intentRouter = AGENTS.find((a) => a.id === 'intent-router')!;
    const knowledgeAgent = AGENTS.find((a) => a.id === 'knowledge-agent')!;
    const playbookAgent = AGENTS.find((a) => a.id === 'playbook-agent')!;
    const builderAgent = AGENTS.find((a) => a.id === 'builder-agent')!;
    const criticAgent = AGENTS.find((a) => a.id === 'critic-qa-agent')!;
    const memoryAgent = AGENTS.find((a) => a.id === 'memory-agent')!;
    const approvalAgent = AGENTS.find((a) => a.id === 'approval-agent')!;

    setIsProcessing(true);
    setActiveAgents(AGENTS.map((a) => ({ ...a, state: 'idle' as const })));

    setActiveAgents((prev) => prev.map((a) => a.id === 'chief-agent' ? { ...a, state: 'thinking' as const } : a));
    addActivity({ agentId: chiefAgent.id, agentName: chiefAgent.name, message: `Received command: "${command}"`, type: 'thinking' });
    await sleep(1200);

    setCurrentHandoff({ from: chiefAgent, to: intentRouter });
    setAgentState('chief-agent', 'idle');
    setAgentState('intent-router', 'thinking');
    addActivity({ agentId: intentRouter.id, agentName: intentRouter.name, message: 'Classifying intent and detecting task domain...', type: 'handoff' });
    await sleep(1400);

    setCurrentHandoff({ from: intentRouter, to: knowledgeAgent });
    setAgentState('intent-router', 'idle');
    setAgentState('knowledge-agent', 'retrieving_memory');
    addActivity({ agentId: knowledgeAgent.id, agentName: knowledgeAgent.name, message: 'Retrieving relevant context from memory store...', type: 'memory' });
    await sleep(1600);

    setCurrentHandoff({ from: knowledgeAgent, to: playbookAgent });
    setAgentState('knowledge-agent', 'idle');
    setAgentState('playbook-agent', 'selecting_playbook');
    addActivity({ agentId: playbookAgent.id, agentName: playbookAgent.name, message: 'Selecting optimal playbook for task...', type: 'playbook' });
    await sleep(1200);

    setCurrentHandoff({ from: playbookAgent, to: builderAgent });
    setAgentState('playbook-agent', 'idle');
    setAgentState('builder-agent', 'building_output');
    addActivity({ agentId: builderAgent.id, agentName: builderAgent.name, message: 'Executing task and building output...', type: 'handoff' });
    await sleep(2000);

    if (isRisky) {
      setCurrentHandoff({ from: builderAgent, to: approvalAgent });
      setAgentState('builder-agent', 'waiting_approval');
      setAgentState('approval-agent', 'waiting_approval');
      addActivity({ agentId: approvalAgent.id, agentName: approvalAgent.name, message: 'Risky action detected. Approval required before proceeding.', type: 'approval' });
      await sleep(1500);
      setAgentState('approval-agent', 'idle');
    }

    setCurrentHandoff({ from: builderAgent, to: criticAgent });
    setAgentState('builder-agent', 'idle');
    setAgentState('critic-qa-agent', 'reviewing');
    addActivity({ agentId: criticAgent.id, agentName: criticAgent.name, message: 'Reviewing output quality and accuracy...', type: 'thinking' });
    await sleep(1400);

    setCurrentHandoff({ from: criticAgent, to: memoryAgent });
    setAgentState('critic-qa-agent', 'idle');
    setAgentState('memory-agent', 'building_output');
    addActivity({ agentId: memoryAgent.id, agentName: memoryAgent.name, message: 'Saving context and results to memory store...', type: 'memory' });
    await sleep(1000);

    setAgentState('memory-agent', 'completed');
    setCurrentHandoff(null);
    addActivity({ agentId: chiefAgent.id, agentName: chiefAgent.name, message: `Task completed successfully. ${isRisky ? 'Approval item created.' : 'Output ready.'}`, type: 'complete' });
    await sleep(800);

    setActiveAgents([]);
    setIsProcessing(false);
  }, [addActivity, setAgentState]);

  const handleSubmit = useCallback((command: string) => {
    runPipeline(command);
  }, [runPipeline]);

  return (
    <div className="min-h-screen p-6 lg:p-8">
      <div className="max-w-5xl mx-auto space-y-8">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center space-y-2"
        >
          <h1 className="text-2xl font-bold text-white/90">Command Center</h1>
          <p className="text-sm text-white/35">
            Issue any command. The agent world will orchestrate the rest.
          </p>
        </motion.div>

        <CommandOrb onSubmit={handleSubmit} isProcessing={isProcessing} />

        <AnimatePresence>
          {currentHandoff && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="bg-black/40 backdrop-blur-sm border border-white/10 rounded-xl p-4"
            >
              <p className="text-xs text-white/40 mb-3">Active Handoff</p>
              <HandoffLine
                fromAgent={currentHandoff.from}
                toAgent={currentHandoff.to}
                isActive={isProcessing}
              />
            </motion.div>
          )}
        </AnimatePresence>

        <AnimatePresence>
          {activeAgents.length > 0 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="bg-black/40 backdrop-blur-sm border border-white/10 rounded-xl p-4"
            >
              <p className="text-xs text-white/40 mb-3">Agent Pipeline</p>
              <div className="grid grid-cols-3 sm:grid-cols-5 lg:grid-cols-9 gap-2">
                {activeAgents.map((agent) => {
                  const stateColor = getStateColor(agent.state);
                  return (
                    <motion.div
                      key={agent.id}
                      animate={
                        agent.state !== 'idle'
                          ? { scale: [1, 1.05, 1] }
                          : { scale: 1 }
                      }
                      transition={{ duration: 1, repeat: agent.state !== 'idle' ? Infinity : 0 }}
                      className="flex flex-col items-center gap-1.5 p-2 rounded-lg bg-white/5 border border-white/5"
                    >
                      <div
                        className="w-2 h-2 rounded-full"
                        style={{ backgroundColor: stateColor }}
                      />
                      <span className="text-white/50 text-center leading-tight" style={{ fontSize: '10px' }}>
                        {agent.name.split(' ')[0]}
                      </span>
                    </motion.div>
                  );
                })}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {activity.length > 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="bg-black/40 backdrop-blur-sm border border-white/10 rounded-xl p-4"
          >
            <div className="flex items-center gap-2 mb-4">
              <Activity className="w-4 h-4 text-indigo-400" />
              <h2 className="text-sm font-medium text-white/70">Activity Stream</h2>
            </div>
            <ActivityStream entries={activity} />
          </motion.div>
        )}

        {activity.length === 0 && !isProcessing && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-16 space-y-4"
          >
            <Sparkles className="w-8 h-8 text-indigo-500/40 mx-auto" />
            <p className="text-sm text-white/25">
              Enter a command above to activate the agent pipeline
            </p>
            <div className="flex flex-wrap gap-2 justify-center mt-4">
              {['Research vector databases', 'Build an automation workflow', 'Create a business model', 'Compare AI frameworks'].map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => handleSubmit(suggestion)}
                  className="text-xs px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 text-white/40 hover:text-white/70 hover:bg-white/10 transition-all"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
