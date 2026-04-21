'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Keyboard } from 'lucide-react';
import { useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts';
import KeyboardShortcutsModal from '@/components/KeyboardShortcutsModal';

export default function Navigation() {
  const [showShortcuts, setShowShortcuts] = useState(false);

  // Initialize keyboard shortcuts
  useKeyboardShortcuts(() => setShowShortcuts(true));

  return (
    <>
      {/* Glassmorphism Navigation */}
      <nav className="fixed top-0 w-full z-50 border-b border-white/5 bg-background/80 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center transform group-hover:scale-105 transition-transform">
              <svg 
                className="w-6 h-6 text-white" 
                fill="none" 
                viewBox="0 0 24 24" 
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3" />
              </svg>
            </div>
            <span className="text-xl font-bold font-display bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
              Veritas AI
            </span>
          </Link>

          {/* Navigation Links */}
          <div className="flex items-center gap-1">
            <NavLink href="/query" label="Query" />
            <NavLink href="/upload" label="Upload" />
            <NavLink href="/documents" label="Documents" />
            <NavLink href="/history" label="History" />
            
            {/* Keyboard Shortcuts Button */}
            <button
              onClick={() => setShowShortcuts(true)}
              className="ml-2 p-2 glass rounded-lg hover:bg-white/10 transition-all"
              title="Keyboard shortcuts (Shift + ?)"
              aria-label="Show keyboard shortcuts"
            >
              <Keyboard className="w-4 h-4 text-secondary" />
            </button>

            {/* API Docs Link */}
            <a
              href="http://localhost:8000/api/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="ml-2 px-4 py-2 text-sm font-medium text-secondary hover:text-primary transition-colors"
            >
              API Docs ↗
            </a>
          </div>
        </div>
      </nav>

      {/* Keyboard Shortcuts Modal */}
      <KeyboardShortcutsModal
        isOpen={showShortcuts}
        onClose={() => setShowShortcuts(false)}
      />
    </>
  );
}

function NavLink({ href, label }: { href: string; label: string }) {
  return (
    <Link 
      href={href}
      className="relative px-4 py-2 rounded-lg text-sm font-medium text-secondary hover:text-primary hover:bg-white/5 transition-all group"
    >
      {label}
      <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-gradient-to-r from-blue-500 to-purple-600 group-hover:w-full transition-all duration-300" />
    </Link>
  );
}
