'use client';

import { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Sparkles } from 'lucide-react';

interface CommandOrbProps {
  onSubmit: (command: string) => void;
  isProcessing: boolean;
}

export default function CommandOrb({ onSubmit, isProcessing }: CommandOrbProps) {
  const [value, setValue] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = () => {
    if (!value.trim() || isProcessing) return;
    onSubmit(value.trim());
    setValue('');
  };

  return (
    <div className="relative">
      <motion.div
        animate={
          isProcessing
            ? { scale: [1, 1.02, 1], opacity: [0.6, 1, 0.6] }
            : { scale: 1, opacity: 1 }
        }
        transition={{ duration: 2, repeat: isProcessing ? Infinity : 0 }}
        className="absolute -inset-px rounded-2xl"
        style={{
          background: isProcessing
            ? 'linear-gradient(135deg, #6366f1, #8b5cf6, #06b6d4, #6366f1)'
            : 'linear-gradient(135deg, #6366f130, #8b5cf630)',
          backgroundSize: '300% 300%',
        }}
      />

      <div className="relative bg-black/60 backdrop-blur-xl rounded-2xl border border-white/10 overflow-hidden">
        <div className="flex items-center gap-3 px-4 py-3">
          <motion.div
            animate={isProcessing ? { rotate: 360 } : { rotate: 0 }}
            transition={{ duration: 2, repeat: isProcessing ? Infinity : 0, ease: 'linear' }}
          >
            <Sparkles
              className="w-5 h-5 flex-shrink-0"
              style={{ color: isProcessing ? '#6366f1' : '#ffffff40' }}
            />
          </motion.div>

          <input
            ref={inputRef}
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
            placeholder="What do you want to build, research, or create?"
            disabled={isProcessing}
            className="flex-1 bg-transparent text-sm text-white placeholder-white/25 outline-none disabled:opacity-50"
          />

          <AnimatePresence>
            {value.trim() && (
              <motion.button
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0, opacity: 0 }}
                onClick={handleSubmit}
                disabled={isProcessing}
                className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center hover:bg-indigo-500 transition-colors disabled:opacity-50"
              >
                <Send className="w-3.5 h-3.5 text-white" />
              </motion.button>
            )}
          </AnimatePresence>
        </div>

        <AnimatePresence>
          {isProcessing && (
            <motion.div
              initial={{ scaleX: 0 }}
              animate={{ scaleX: 1 }}
              exit={{ scaleX: 0 }}
              transition={{ duration: 8, ease: 'linear' }}
              className="h-0.5 origin-left bg-gradient-to-r from-indigo-500 via-purple-500 to-cyan-500"
            />
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
