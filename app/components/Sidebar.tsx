'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion } from 'framer-motion';
import {
  Terminal,
  Users,
  FolderOpen,
  Brain,
  BookOpen,
  ShieldAlert,
  ScrollText,
  Zap,
} from 'lucide-react';
import { cn } from '@/app/lib/utils';

const NAV_ITEMS = [
  { href: '/command', label: 'Command', icon: Terminal },
  { href: '/agents', label: 'Agents', icon: Users },
  { href: '/projects', label: 'Projects', icon: FolderOpen },
  { href: '/memory', label: 'Memory', icon: Brain },
  { href: '/playbooks', label: 'Playbooks', icon: BookOpen },
  { href: '/approvals', label: 'Approvals', icon: ShieldAlert },
  { href: '/logs', label: 'Logs', icon: ScrollText },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 h-full w-16 lg:w-56 bg-black/40 backdrop-blur-xl border-r border-white/5 z-50 flex flex-col">
      <div className="p-4 flex items-center gap-3 border-b border-white/5">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 8, repeat: Infinity, ease: 'linear' }}
          className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center flex-shrink-0"
        >
          <Zap className="w-4 h-4 text-white" />
        </motion.div>
        <span className="hidden lg:block text-sm font-semibold text-white/90 truncate">Agent World</span>
      </div>

      <nav className="flex-1 p-2 space-y-1">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link key={item.href} href={item.href}>
              <motion.div
                whileHover={{ x: 3 }}
                className={cn(
                  'flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 group',
                  isActive
                    ? 'bg-indigo-600/20 text-indigo-400 border border-indigo-500/20'
                    : 'text-white/40 hover:text-white/80 hover:bg-white/5'
                )}
              >
                <Icon className="w-4 h-4 flex-shrink-0" />
                <span className="hidden lg:block text-sm">{item.label}</span>
                {isActive && (
                  <motion.div
                    layoutId="activeIndicator"
                    className="hidden lg:block ml-auto w-1.5 h-1.5 rounded-full bg-indigo-400"
                  />
                )}
              </motion.div>
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-white/5">
        <div className="hidden lg:flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-xs text-white/30">System Online</span>
        </div>
        <div className="lg:hidden flex justify-center">
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
        </div>
      </div>
    </aside>
  );
}
