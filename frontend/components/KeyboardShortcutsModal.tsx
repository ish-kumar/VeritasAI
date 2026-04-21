'use client';

import { X, Keyboard, Command } from 'lucide-react';
import { useEffect } from 'react';

interface KeyboardShortcutsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function KeyboardShortcutsModal({ isOpen, onClose }: KeyboardShortcutsModalProps) {
  useEffect(() => {
    if (!isOpen) return;

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const shortcuts = [
    {
      category: 'Navigation',
      items: [
        { keys: ['G', 'H'], description: 'Go to Home' },
        { keys: ['G', 'Q'], description: 'Go to Query' },
        { keys: ['G', 'U'], description: 'Go to Upload' },
        { keys: ['G', 'D'], description: 'Go to Documents' },
        { keys: ['G', 'R'], description: 'Go to History' },
      ],
    },
    {
      category: 'Actions',
      items: [
        { keys: ['/'], description: 'Focus search input' },
        { keys: ['?'], description: 'Show keyboard shortcuts' },
        { keys: ['Esc'], description: 'Close modals/dialogs' },
      ],
    },
    {
      category: 'Query Page',
      items: [
        { keys: ['Enter'], description: 'Submit query' },
        { keys: ['Shift', 'Enter'], description: 'New line in query' },
        { keys: ['Ctrl', 'K'], description: 'Clear query (Mac: ⌘K)' },
      ],
    },
  ];

  const isMac = typeof window !== 'undefined' && navigator.platform.toUpperCase().indexOf('MAC') >= 0;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 animate-fade-in"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none">
        <div
          className="glass border border-white/10 rounded-2xl max-w-2xl w-full max-h-[80vh] overflow-y-auto pointer-events-auto animate-fade-in-up"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="sticky top-0 bg-surface border-b border-white/10 p-6 flex items-center justify-between z-10">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 flex items-center justify-center">
                <Keyboard className="w-5 h-5 text-blue-400" />
              </div>
              <h2 className="text-2xl font-bold">Keyboard Shortcuts</h2>
            </div>
            <button
              onClick={onClose}
              className="p-2 glass rounded-lg hover:bg-white/10 transition-all"
              aria-label="Close modal"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Content */}
          <div className="p-6 space-y-8">
            {shortcuts.map((section, idx) => (
              <div key={section.category} className="animate-fade-in-up" style={{ animationDelay: `${idx * 50}ms` }}>
                <h3 className="text-lg font-semibold mb-4 text-secondary">
                  {section.category}
                </h3>
                <div className="space-y-2">
                  {section.items.map((shortcut, itemIdx) => (
                    <div
                      key={itemIdx}
                      className="flex items-start justify-between gap-6 p-4 glass rounded-xl hover:bg-white/5 transition-all min-h-[48px]"
                    >
                      <span className="text-sm font-medium flex-1 py-1">{shortcut.description}</span>
                      <div className="flex items-center gap-1.5 flex-shrink-0 ml-auto">
                        {shortcut.keys.map((key, keyIdx) => (
                          <span key={keyIdx} className="inline-flex items-center gap-1.5">
                            <kbd className="px-3 py-1.5 text-xs font-mono bg-white/10 border border-white/20 rounded whitespace-nowrap">
                              {key === 'Ctrl' && isMac ? '⌘' : key}
                            </kbd>
                            {keyIdx < shortcut.keys.length - 1 && (
                              <span className="text-muted text-xs whitespace-nowrap px-1">then</span>
                            )}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* Footer */}
          <div className="sticky bottom-0 bg-surface border-t border-white/10 p-4 z-10">
            <p className="text-xs text-center text-muted">
              Press <kbd className="px-1.5 py-0.5 text-xs bg-white/10 border border-white/20 rounded">?</kbd> anytime to view shortcuts
            </p>
          </div>
        </div>
      </div>
    </>
  );
}
