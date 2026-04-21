'use client';

import Link from 'next/link';
import { FileQuestion, Home, ArrowLeft, Search } from 'lucide-react';

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center px-8 py-12">
      <div className="max-w-2xl mx-auto text-center">
        {/* Icon */}
        <div className="mb-8 animate-fade-in">
          <div className="w-24 h-24 rounded-2xl bg-gradient-to-br from-rose-500/20 to-purple-500/20 flex items-center justify-center mx-auto">
            <FileQuestion className="w-12 h-12 text-rose-400" />
          </div>
        </div>

        {/* Error Code */}
        <div className="mb-6 animate-fade-in-up" style={{ animationDelay: '100ms' }}>
          <h1 className="text-8xl md:text-9xl font-bold gradient-text mb-4">
            404
          </h1>
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Page Not Found
          </h2>
          <p className="text-xl text-secondary max-w-md mx-auto">
            The page you're looking for doesn't exist or has been moved.
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center animate-fade-in-up" style={{ animationDelay: '200ms' }}>
          <Link
            href="/"
            className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl font-semibold hover:shadow-lg hover:shadow-blue-500/25 transition-all button-press"
          >
            <Home className="w-5 h-5" />
            Back to Home
          </Link>
          
          <Link
            href="/query"
            className="inline-flex items-center gap-2 px-6 py-3 glass border border-white/10 rounded-xl font-semibold hover:bg-white/10 transition-all"
          >
            <Search className="w-5 h-5" />
            Search Documents
          </Link>
        </div>

        {/* Helpful Links */}
        <div className="mt-12 p-6 glass border border-white/10 rounded-2xl animate-fade-in-up" style={{ animationDelay: '300ms' }}>
          <h3 className="text-lg font-semibold mb-4">Helpful Links</h3>
          <div className="grid grid-cols-2 gap-3 text-sm">
            <Link
              href="/"
              className="text-secondary hover:text-primary transition-colors flex items-center gap-2"
            >
              <Home className="w-4 h-4" />
              Dashboard
            </Link>
            <Link
              href="/query"
              className="text-secondary hover:text-primary transition-colors flex items-center gap-2"
            >
              <Search className="w-4 h-4" />
              Query Interface
            </Link>
            <Link
              href="/upload"
              className="text-secondary hover:text-primary transition-colors flex items-center gap-2"
            >
              <FileQuestion className="w-4 h-4" />
              Upload Documents
            </Link>
            <Link
              href="/documents"
              className="text-secondary hover:text-primary transition-colors flex items-center gap-2"
            >
              <FileQuestion className="w-4 h-4" />
              Manage Documents
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
