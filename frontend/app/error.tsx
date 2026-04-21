'use client';

import { useEffect } from 'react';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';
import Link from 'next/link';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error('Application error:', error);
  }, [error]);

  return (
    <div className="min-h-screen flex items-center justify-center px-8 py-12">
      <div className="max-w-2xl mx-auto text-center">
        {/* Icon */}
        <div className="mb-8 animate-fade-in">
          <div className="w-24 h-24 rounded-2xl bg-gradient-to-br from-rose-500/20 to-amber-500/20 flex items-center justify-center mx-auto">
            <AlertTriangle className="w-12 h-12 text-rose-400" />
          </div>
        </div>

        {/* Error Message */}
        <div className="mb-6 animate-fade-in-up" style={{ animationDelay: '100ms' }}>
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            Something went wrong
          </h1>
          <p className="text-xl text-secondary max-w-md mx-auto mb-4">
            We encountered an unexpected error. This has been logged and we'll look into it.
          </p>
          
          {/* Error Details (only in development) */}
          {process.env.NODE_ENV === 'development' && (
            <div className="mt-6 p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl text-left">
              <p className="text-xs text-rose-400 font-mono break-all">
                {error.message}
              </p>
              {error.digest && (
                <p className="text-xs text-muted mt-2">
                  Error ID: {error.digest}
                </p>
              )}
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center animate-fade-in-up" style={{ animationDelay: '200ms' }}>
          <button
            onClick={reset}
            className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl font-semibold hover:shadow-lg hover:shadow-blue-500/25 transition-all button-press"
          >
            <RefreshCw className="w-5 h-5" />
            Try Again
          </button>
          
          <Link
            href="/"
            className="inline-flex items-center gap-2 px-6 py-3 glass border border-white/10 rounded-xl font-semibold hover:bg-white/10 transition-all"
          >
            <Home className="w-5 h-5" />
            Back to Home
          </Link>
        </div>

        {/* Help Text */}
        <div className="mt-12 p-6 glass border border-white/10 rounded-2xl animate-fade-in-up" style={{ animationDelay: '300ms' }}>
          <p className="text-sm text-secondary">
            If this error persists, please check:
          </p>
          <ul className="text-sm text-secondary mt-3 space-y-2 text-left max-w-md mx-auto">
            <li>• Backend server is running (port 8000)</li>
            <li>• Network connection is stable</li>
            <li>• Browser console for additional errors</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
