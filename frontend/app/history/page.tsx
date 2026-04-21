'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { History, Search, Trash2, AlertTriangle } from 'lucide-react';
import { HistoryTable } from '@/components/HistoryTable';
import { toast } from 'sonner';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";

interface QueryHistoryItem {
  id: string;
  query: string;
  timestamp: number;
  answered: boolean;
  confidence?: number;
  risk?: string;
}

export default function QueryHistoryPage() {
  const [history, setHistory] = useState<QueryHistoryItem[]>([]);
  const [clearDialogOpen, setClearDialogOpen] = useState(false);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = () => {
    try {
      const stored = localStorage.getItem('legalrag_query_history');
      if (stored) {
        const parsed = JSON.parse(stored);
        setHistory(parsed);
      }
    } catch (err) {
      console.error('Failed to load query history:', err);
    }
  };

  const clearHistory = () => {
    toast.promise(
      new Promise<void>((resolve) => {
        localStorage.removeItem('legalrag_query_history');
        setHistory([]);
        resolve();
      }),
      {
        loading: 'Clearing history...',
        success: 'All query history cleared',
        error: 'Failed to clear history',
      }
    );
  };

  const deleteItem = (id: string) => {
    const updated = history.filter(item => item.id !== id);
    localStorage.setItem('legalrag_query_history', JSON.stringify(updated));
    setHistory(updated);
    toast.success('Query deleted from history');
  };

  const formatDate = (timestamp: number) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="min-h-screen px-8 py-12">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-12 animate-fade-in">
          <div>
            <h1 className="text-4xl md:text-5xl font-bold mb-3">Query History</h1>
            <p className="text-xl text-secondary">
              View and revisit your past queries
            </p>
          </div>
          
          {history.length > 0 && (
            <AlertDialog open={clearDialogOpen} onOpenChange={setClearDialogOpen}>
              <AlertDialogTrigger asChild>
                <button
                  className="px-4 py-2 glass rounded-xl hover:bg-white/10 transition-all inline-flex items-center gap-2"
                  aria-label="Clear all history"
                >
                  <Trash2 className="w-4 h-4" />
                  <span className="hidden sm:inline">Clear All</span>
                </button>
              </AlertDialogTrigger>
              <AlertDialogContent className="bg-surface border-white/10">
                <AlertDialogHeader>
                  <AlertDialogTitle className="text-text-primary flex items-center gap-2">
                    <AlertTriangle className="w-5 h-5 text-rose-400" />
                    Clear All Query History?
                  </AlertDialogTitle>
                  <AlertDialogDescription className="text-secondary">
                    <div className="space-y-3 mt-4">
                      <p>You are about to permanently delete <strong className="text-text-primary">{history.length} quer{history.length === 1 ? 'y' : 'ies'}</strong> from your local browser history.</p>
                      <div className="p-3 rounded-lg bg-amber-500/10 border border-amber-500/20">
                        <p className="text-amber-400 text-sm">
                          <strong>Warning:</strong> This action cannot be undone. Your query history will be completely cleared.
                        </p>
                      </div>
                    </div>
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel className="bg-surface border-white/10 text-text-primary hover:bg-white/5">
                    Cancel
                  </AlertDialogCancel>
                  <AlertDialogAction
                    onClick={clearHistory}
                    className="bg-rose-600 hover:bg-rose-500 text-white"
                  >
                    Clear All History
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          )}
        </div>

        {/* Empty State */}
        {history.length === 0 ? (
          <div className="glass border border-white/10 rounded-2xl p-16 text-center animate-fade-in">
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 flex items-center justify-center mx-auto mb-6">
              <History className="w-10 h-10 text-blue-400" />
            </div>
            <h2 className="text-3xl font-bold mb-3">No Query History</h2>
            <p className="text-secondary mb-8 max-w-md mx-auto">
              Your past queries will appear here. Submit your first query to get started!
            </p>
            <Link
              href="/query"
              className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl font-semibold hover:shadow-lg hover:shadow-blue-500/25 transition-all button-press"
            >
              <Search className="w-5 h-5" />
              Start Querying
            </Link>
          </div>
        ) : (
          /* History Table */
          <div className="space-y-6 animate-fade-in-up">
            <HistoryTable
              history={history}
              onDelete={deleteItem}
              formatDate={formatDate}
            />
          </div>
        )}

        {/* Info */}
        {history.length > 0 && (
          <div className="mt-8 p-4 glass border border-white/10 rounded-xl">
            <p className="text-sm text-muted text-center">
              History is stored locally in your browser. Click any query to re-run it.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
