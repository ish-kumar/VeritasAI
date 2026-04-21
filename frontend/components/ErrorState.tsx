'use client';

import { AlertTriangle, WifiOff, RefreshCw } from 'lucide-react';

interface ErrorStateProps {
  title?: string;
  message: string;
  type?: 'error' | 'network' | 'timeout';
  onRetry?: () => void;
  retrying?: boolean;
}

export default function ErrorState({ 
  title, 
  message, 
  type = 'error',
  onRetry,
  retrying = false
}: ErrorStateProps) {
  const getIcon = () => {
    switch (type) {
      case 'network':
        return <WifiOff className="w-8 h-8 text-rose-400" />;
      case 'timeout':
        return <AlertTriangle className="w-8 h-8 text-amber-400" />;
      default:
        return <AlertTriangle className="w-8 h-8 text-rose-400" />;
    }
  };

  const getColor = () => {
    switch (type) {
      case 'timeout':
        return 'amber';
      default:
        return 'rose';
    }
  };

  const color = getColor();

  return (
    <div className={`p-6 rounded-2xl bg-${color}-500/10 border border-${color}-500/20 animate-fade-in`}>
      <div className="flex items-start gap-4">
        <div className={`w-12 h-12 rounded-xl bg-gradient-to-br from-${color}-500/20 to-${color}-600/20 flex items-center justify-center flex-shrink-0`}>
          {getIcon()}
        </div>
        
        <div className="flex-1">
          {title && (
            <h3 className={`text-lg font-semibold mb-1 text-${color}-400`}>
              {title}
            </h3>
          )}
          <p className={`text-sm text-${color}-400/90`}>
            {message}
          </p>
          
          {onRetry && (
            <button
              onClick={onRetry}
              disabled={retrying}
              className={`mt-4 inline-flex items-center gap-2 px-4 py-2 bg-${color}-500/20 hover:bg-${color}-500/30 rounded-lg text-sm font-medium transition-all disabled:opacity-50`}
              aria-label="Retry action"
            >
              <RefreshCw className={`w-4 h-4 ${retrying ? 'animate-spin' : ''}`} />
              {retrying ? 'Retrying...' : 'Try Again'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
