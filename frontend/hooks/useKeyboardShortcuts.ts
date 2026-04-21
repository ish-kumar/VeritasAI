'use client';

import { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';

export function useKeyboardShortcuts(onShowShortcuts: () => void) {
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    let sequenceKeys: string[] = [];
    let sequenceTimeout: NodeJS.Timeout | null = null;

    const handleKeyDown = (e: KeyboardEvent) => {
      // Ignore if user is typing in an input/textarea
      const target = e.target as HTMLElement;
      if (
        target.tagName === 'INPUT' ||
        target.tagName === 'TEXTAREA' ||
        target.isContentEditable
      ) {
        // Allow some shortcuts even in inputs
        if (e.key === '?' && !e.shiftKey) {
          // Don't show shortcuts while typing
          return;
        }
        return;
      }

      // Show shortcuts modal
      if (e.key === '?' && e.shiftKey) {
        e.preventDefault();
        onShowShortcuts();
        return;
      }

      // Focus search input
      if (e.key === '/') {
        e.preventDefault();
        const searchInput = document.querySelector('textarea[placeholder*="query"]') as HTMLTextAreaElement;
        if (searchInput) {
          searchInput.focus();
        }
        return;
      }

      // Handle 'G' sequence for navigation
      if (e.key.toLowerCase() === 'g') {
        sequenceKeys.push('g');
        
        if (sequenceTimeout) {
          clearTimeout(sequenceTimeout);
        }

        // Wait for second key
        sequenceTimeout = setTimeout(() => {
          sequenceKeys = [];
        }, 1000);

        return;
      }

      // Navigation shortcuts (after 'G')
      if (sequenceKeys.includes('g')) {
        e.preventDefault();
        
        switch (e.key.toLowerCase()) {
          case 'h':
            router.push('/');
            break;
          case 'q':
            router.push('/query');
            break;
          case 'u':
            router.push('/upload');
            break;
          case 'd':
            router.push('/documents');
            break;
          case 'r':
            router.push('/history');
            break;
        }

        sequenceKeys = [];
        if (sequenceTimeout) {
          clearTimeout(sequenceTimeout);
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      if (sequenceTimeout) {
        clearTimeout(sequenceTimeout);
      }
    };
  }, [router, pathname, onShowShortcuts]);
}
