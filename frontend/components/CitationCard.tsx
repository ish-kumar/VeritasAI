/**
 * Citation Card Component
 * 
 * Displays a single citation with:
 * - Clause ID
 * - Quoted text
 * - Reasoning
 * - Verification status (valid/invalid)
 */

import { Quote, CheckCircle, XCircle, FileText } from 'lucide-react';

interface Citation {
  clause_id: string;
  quoted_text: string;
  reasoning: string;
  document_id?: string;
}

interface CitationCardProps {
  citation: Citation;
  isValid?: boolean;
  index: number;
}

export function CitationCard({ citation, isValid = true, index }: CitationCardProps) {
  return (
    <div className={`p-5 rounded-xl glass border transition-all hover:scale-[1.02] ${
      isValid 
        ? 'border-emerald-500/20 hover:border-emerald-500/30' 
        : 'border-rose-500/20 hover:border-rose-500/30'
    }`}>
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500/20 to-purple-500/20 flex items-center justify-center flex-shrink-0">
            <Quote className="w-4 h-4 text-blue-400" />
          </div>
          <div>
            <span className="text-xs text-muted uppercase tracking-wider">Citation {index + 1}</span>
            <div className="font-mono text-sm text-secondary">
              {citation.clause_id}
            </div>
            {citation.document_id && (
              <div className="flex items-center gap-1.5 mt-1">
                <FileText className="w-3 h-3 text-blue-400" />
                <span className="text-xs text-blue-400 font-medium">
                  From: {citation.document_id}
                </span>
              </div>
            )}
          </div>
        </div>
        
        {/* Verification Badge */}
        {isValid ? (
          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20">
            <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
            <span className="text-xs text-emerald-400 font-medium">Verified</span>
          </div>
        ) : (
          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-rose-500/10 border border-rose-500/20">
            <XCircle className="w-3.5 h-3.5 text-rose-400" />
            <span className="text-xs text-rose-400 font-medium">Invalid</span>
          </div>
        )}
      </div>

      {/* Quoted Text */}
      <div className="relative pl-4 mb-4">
        <div className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-blue-500 to-purple-600 rounded-full" />
        <p className="text-sm italic leading-relaxed text-primary">
          "{citation.quoted_text}"
        </p>
      </div>

      {/* Reasoning */}
      <div className="pt-4 border-t border-white/5">
        <span className="text-xs text-secondary uppercase tracking-wider">Reasoning</span>
        <p className="text-sm text-secondary mt-2 leading-relaxed">
          {citation.reasoning}
        </p>
      </div>
    </div>
  );
}
