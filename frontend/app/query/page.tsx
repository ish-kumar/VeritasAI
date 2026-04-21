/**
 * Query Page - Veritas AI Interface
 * 
 * Submit queries and view results with:
 * - Confidence meter
 * - Risk badge
 * - Citations (verified)
 * - Counter-arguments
 * - Warnings
 */

'use client';

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { api, QueryResponse } from '@/lib/api';
import { ConfidenceMeter } from '@/components/ConfidenceMeter';
import { RiskBadge } from '@/components/RiskBadge';
import { CitationCard } from '@/components/CitationCard';
import { CounterArgumentCard } from '@/components/CounterArgumentCard';
import { useQueryHistory } from '@/hooks/useQueryHistory';
import { LegalQueryInput } from '@/components/ui/legal-query-input';
import { Search, Loader2, X, AlertTriangle, CheckCircle, ShieldAlert, ChevronDown } from 'lucide-react';

export default function QueryPage() {
  const searchParams = useSearchParams();
  const [query, setQuery] = useState('');
  const [jurisdiction, setJurisdiction] = useState('');
  const [result, setResult] = useState<QueryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const { saveQuery } = useQueryHistory();

  // Load query from URL params (for history links)
  useEffect(() => {
    const qParam = searchParams.get('q');
    if (qParam) {
      setQuery(qParam);
    }
  }, [searchParams]);

  const handleSubmit = async () => {
    if (!query.trim()) {
      setError('Please enter a query');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const response = await api.submitQuery({
        query: query.trim(),
        jurisdiction: jurisdiction || undefined,
      });
      setResult(response);

      // Save to history
      saveQuery(
        query.trim(),
        !!response.answer, // Convert to boolean
        response.confidence?.overall_score,
        response.risk?.overall_risk
      );
    } catch (err: any) {
      console.error('Query failed:', err);
      setError(err.response?.data?.detail || 'Failed to process query. Is the backend running?');
      
      // Save failed query to history too
      saveQuery(query.trim(), false);
    } finally {
      setLoading(false);
    }
  };

  const clearResults = () => {
    setResult(null);
    setQuery('');
    setJurisdiction('');
    setError(null);
  };

  return (
    <div className="min-h-screen px-8 py-12">
      <div className="max-w-6xl mx-auto">
        {/* Header - Only show when no results */}
        {!result && (
          <div className="text-center mb-12 animate-fade-in">
            <h1 className="text-4xl md:text-5xl font-bold mb-3">Legal Query Interface</h1>
            <p className="text-xl text-secondary max-w-2xl mx-auto">
              Ask questions about your legal documents with AI-powered semantic search
            </p>
          </div>
        )}

        {/* Query Input - Vertically centered when empty, compact at top when results */}
        <div className={`
          transition-all duration-700 ease-out relative
          ${!result 
            ? 'min-h-[60vh] flex items-center justify-center' 
            : 'mb-12'
          }
        `}>
          <div className={`
            w-full transition-all duration-700 ease-out
            ${!result 
              ? 'max-w-4xl mx-auto' 
              : 'max-w-4xl mx-auto'
            }
          `}>
            <form onSubmit={(e) => { e.preventDefault(); handleSubmit(); }} className="animate-fade-in-up">
              {/* Compact header when results are showing */}
              {result && (
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold">Legal Query</h2>
                  <button
                    type="button"
                    onClick={clearResults}
                    className="px-4 py-2 glass rounded-xl text-sm font-medium hover:bg-white/10 transition-all inline-flex items-center gap-2"
                    title="Start a new query"
                  >
                    <X className="w-4 h-4" />
                    <span>New Query</span>
                  </button>
                </div>
              )}

              {/* New Animated Legal Query Input - Clean, no AI slop */}
              <LegalQueryInput
                value={query}
                onChange={setQuery}
                onSubmit={handleSubmit}
                isLoading={loading}
                disabled={loading}
                placeholder="Ask a legal question... (e.g., What are the termination clauses?)"
              />

              {/* Hint text */}
              <p id="query-hint" className="text-xs text-muted mt-6 text-center">
                Press <kbd className="px-1.5 py-0.5 text-xs bg-white/10 border border-white/20 rounded">Enter</kbd> to submit • <kbd className="px-1.5 py-0.5 text-xs bg-white/10 border border-white/20 rounded">Shift</kbd> + <kbd className="px-1.5 py-0.5 text-xs bg-white/10 border border-white/20 rounded">Enter</kbd> for new line
              </p>

              {/* Advanced Options (Collapsible) */}
              <div className="mt-6">
                <button
                  type="button"
                  onClick={() => setShowAdvanced(!showAdvanced)}
                  className="text-sm text-secondary hover:text-primary transition-colors inline-flex items-center gap-1"
                >
                  Advanced Options
                  <ChevronDown className={`w-4 h-4 transition-transform ${showAdvanced ? 'rotate-180' : ''}`} />
                </button>

                {showAdvanced && (
                  <div className="mt-3 p-4 rounded-xl glass border border-white/10 animate-fade-in">
                    <label className="block text-sm font-medium mb-2 text-secondary">
                      Jurisdiction (Optional)
                    </label>
                    <input
                      type="text"
                      value={jurisdiction}
                      onChange={(e) => setJurisdiction(e.target.value)}
                      placeholder="E.g., California, New York, Federal"
                      className="w-full px-4 py-2 rounded-lg glass border border-white/10 focus:border-blue-500/50 focus:ring-2 focus:ring-blue-500/10 transition-all placeholder-secondary"
                      disabled={loading}
                    />
                  </div>
                )}
              </div>
            </form>

            {/* Helpful hints when no results */}
            {!result && !loading && (
              <div className="mt-12 text-center animate-fade-in delay-300">
                <p className="text-sm text-muted mb-4">Try asking:</p>
                <div className="flex flex-wrap gap-2 justify-center">
                  {[
                    "What are the termination clauses?",
                    "What is the base salary?",
                    "How are disputes resolved?",
                    "What are the confidentiality terms?"
                  ].map((example, i) => (
                    <button
                      key={i}
                      type="button"
                      onClick={() => setQuery(example)}
                      className="px-4 py-2 text-sm glass rounded-lg hover:bg-white/10 transition-all hover:scale-105"
                    >
                      {example}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-12 p-6 rounded-2xl bg-rose-500/10 border border-rose-500/20 animate-fade-in max-w-4xl mx-auto">
            <div className="flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-rose-400 mt-0.5 flex-shrink-0" />
              <p className="text-rose-400">{error}</p>
            </div>
          </div>
        )}

        {/* Results */}
        {result && (
          <div className="space-y-6 animate-fade-in-up">
            {/* Show metrics ONLY if query succeeded */}
            {result.success && result.answer && (
              <div className="glass p-6 rounded-2xl border border-white/10 shadow-2xl animate-fade-in">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-semibold">Analysis Complete</h2>
                  <span className="text-xs text-muted font-mono px-3 py-1 rounded-full glass">
                    ID: {result.query_id}
                  </span>
                </div>

                {/* Confidence & Risk */}
                <div className="grid md:grid-cols-2 gap-6">
                  {result.confidence && (
                    <ConfidenceMeter score={result.confidence.overall_score} />
                  )}

                  {result.risk && (
                    <div className="flex flex-col justify-center">
                      <span className="text-sm font-medium text-secondary mb-3">Risk Assessment</span>
                      <RiskBadge level={result.risk.overall_risk} size="lg" />
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Answer or Refusal */}
            {result.success && result.answer ? (
              <div className="space-y-6">
                {/* Main Answer */}
                <div className="p-8 rounded-2xl glass border border-white/10 animate-fade-in-up delay-100">
                  <div className="flex items-center gap-3 mb-4">
                    <CheckCircle className="w-6 h-6 text-emerald-400" />
                    <h3 className="text-2xl font-bold">Answer</h3>
                  </div>
                  <p className="text-lg leading-relaxed text-primary mb-6">
                    {result.answer.answer_text}
                  </p>

                  {/* Reasoning */}
                  {result.answer.reasoning && (
                    <div className="mt-6 pt-6 border-t border-white/10">
                      <h4 className="text-sm font-semibold text-secondary uppercase tracking-wider mb-3">Reasoning</h4>
                      <p className="text-sm text-secondary leading-relaxed">{result.answer.reasoning}</p>
                    </div>
                  )}

                  {/* Assumptions & Caveats */}
                  {(result.answer.assumptions?.length > 0 || result.answer.caveats?.length > 0) && (
                    <div className="mt-6 pt-6 border-t border-white/10 grid md:grid-cols-2 gap-6">
                      {result.answer.assumptions?.length > 0 && (
                        <div>
                          <h4 className="text-sm font-semibold text-secondary uppercase tracking-wider mb-3">Assumptions</h4>
                          <ul className="space-y-2">
                            {result.answer.assumptions.map((a, i) => (
                              <li key={i} className="flex gap-2 text-sm text-secondary">
                                <span className="text-blue-400 mt-0.5">•</span>
                                <span>{a}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {result.answer.caveats?.length > 0 && (
                        <div>
                          <h4 className="text-sm font-semibold text-secondary uppercase tracking-wider mb-3">Caveats</h4>
                          <ul className="space-y-2">
                            {result.answer.caveats.map((c, i) => (
                              <li key={i} className="flex gap-2 text-sm text-secondary">
                                <span className="text-amber-400 mt-0.5">•</span>
                                <span>{c}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {/* Citations */}
                {result.answer.citations && result.answer.citations.length > 0 && (
                  <div className="animate-fade-in-up delay-200">
                    <h3 className="text-2xl font-bold mb-4">
                      Citations <span className="text-secondary text-lg">({result.answer.citations.length})</span>
                    </h3>
                    <div className="grid md:grid-cols-2 gap-4">
                      {result.answer.citations.map((citation, i) => (
                        <CitationCard key={i} citation={citation} index={i} />
                      ))}
                    </div>
                  </div>
                )}

                {/* Counter-Argument */}
                {result.counter_arguments && (
                  <div className="animate-fade-in-up delay-300">
                    <h3 className="text-2xl font-bold mb-4">Adversarial Analysis</h3>
                    <CounterArgumentCard counterArgument={result.counter_arguments} />
                  </div>
                )}

                {/* Warnings */}
                {result.warnings && result.warnings.length > 0 && (
                  <div className="p-6 rounded-2xl bg-amber-500/10 border border-amber-500/20 animate-fade-in-up delay-400">
                    <div className="flex items-center gap-3 mb-4">
                      <AlertTriangle className="w-5 h-5 text-amber-400" />
                      <h3 className="text-lg font-semibold text-amber-400">Important Warnings</h3>
                    </div>
                    <ul className="space-y-2">
                      {result.warnings.map((warning, i) => (
                        <li key={i} className="flex gap-2 text-secondary">
                          <span className="text-amber-400 mt-0.5">•</span>
                          <span>{warning}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ) : (
              /* Refusal - Show metrics here too for transparency */
              <div className="space-y-6">
                {/* Show confidence/risk for refused queries too (for transparency) */}
                <div className="glass p-6 rounded-2xl border border-white/10 shadow-2xl animate-fade-in">
                  <div className="flex items-center justify-between mb-6">
                    <h2 className="text-2xl font-semibold">Analysis Complete</h2>
                    <span className="text-xs text-muted font-mono px-3 py-1 rounded-full glass">
                      ID: {result.query_id}
                    </span>
                  </div>

                  {/* Confidence & Risk */}
                  <div className="grid md:grid-cols-2 gap-6">
                    {result.confidence && (
                      <ConfidenceMeter score={result.confidence.overall_score} />
                    )}

                    {result.risk && (
                      <div className="flex flex-col justify-center">
                        <span className="text-sm font-medium text-secondary mb-3">Risk Assessment</span>
                        <RiskBadge level={result.risk.overall_risk} size="lg" />
                      </div>
                    )}
                  </div>
                </div>

                {/* Refusal Card */}
                <div className="p-8 rounded-2xl bg-rose-500/10 border border-rose-500/20 animate-fade-in-up delay-100">
                  <div className="flex items-center gap-3 mb-4">
                    <ShieldAlert className="w-6 h-6 text-rose-400" />
                    <h3 className="text-2xl font-bold text-rose-400">Query Refused</h3>
                  </div>
                  <p className="text-lg leading-relaxed mb-6">
                    {result.refusal_explanation || 'The system cannot provide a confident answer to this query.'}
                  </p>
                  
                  {/* Show why it was refused */}
                  <div className="pt-4 border-t border-rose-500/20">
                    <p className="text-sm text-secondary">
                      <strong>Why was this refused?</strong> The confidence score and risk assessment above indicate this query requires professional legal review. 
                      {result.warnings && result.warnings.length > 0 && ' Additional warnings are listed below.'}
                    </p>
                  </div>
                </div>

                {/* Warnings - After refusal */}
                {result.warnings && result.warnings.length > 0 && (
                  <div className="p-6 rounded-2xl bg-amber-500/10 border border-amber-500/20 animate-fade-in-up delay-200">
                    <div className="flex items-center gap-3 mb-4">
                      <AlertTriangle className="w-5 h-5 text-amber-400" />
                      <h3 className="text-lg font-semibold text-amber-400">Additional Context</h3>
                    </div>
                    <ul className="space-y-2">
                      {result.warnings.map((warning, i) => (
                        <li key={i} className="flex gap-2 text-secondary">
                          <span className="text-amber-400 mt-0.5">•</span>
                          <span>{warning}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
