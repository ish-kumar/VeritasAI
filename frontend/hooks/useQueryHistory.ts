'use client';

interface QueryHistoryItem {
  id: string;
  query: string;
  timestamp: number;
  answered: boolean;
  confidence?: number;
  risk?: string;
}

const MAX_HISTORY_ITEMS = 50;

export function useQueryHistory() {
  const saveQuery = (
    query: string, 
    answered: boolean, 
    confidence?: number, 
    risk?: string
  ) => {
    try {
      const stored = localStorage.getItem('legalrag_query_history');
      const history: QueryHistoryItem[] = stored ? JSON.parse(stored) : [];

      const newItem: QueryHistoryItem = {
        id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        query,
        timestamp: Date.now(),
        answered,
        confidence,
        risk,
      };

      // Add to beginning of array
      const updated = [newItem, ...history].slice(0, MAX_HISTORY_ITEMS);

      localStorage.setItem('legalrag_query_history', JSON.stringify(updated));
    } catch (err) {
      console.error('Failed to save query to history:', err);
    }
  };

  const getHistory = (): QueryHistoryItem[] => {
    try {
      const stored = localStorage.getItem('legalrag_query_history');
      return stored ? JSON.parse(stored) : [];
    } catch (err) {
      console.error('Failed to load query history:', err);
      return [];
    }
  };

  const clearHistory = () => {
    try {
      localStorage.removeItem('legalrag_query_history');
    } catch (err) {
      console.error('Failed to clear query history:', err);
    }
  };

  return { saveQuery, getHistory, clearHistory };
}
