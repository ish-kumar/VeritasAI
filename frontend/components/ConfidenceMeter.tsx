/**
 * Confidence Meter Component
 * 
 * Circular gauge showing the confidence score (0-100).
 * Color-coded: green (85+), yellow (60-84), red (<60)
 */

'use client';

import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface ConfidenceMeterProps {
  score: number;
  label?: string;
  showBreakdown?: boolean;
}

export function ConfidenceMeter({ score, label = "Confidence", showBreakdown = false }: ConfidenceMeterProps) {
  const getColor = (score: number): string => {
    if (score >= 85) return '#34d399'; // emerald-400
    if (score >= 60) return '#fbbf24'; // amber-400
    return '#f43f5e'; // rose-500
  };

  const getGradientId = (score: number): string => {
    if (score >= 85) return 'gradient-high';
    if (score >= 60) return 'gradient-medium';
    return 'gradient-low';
  };

  const getLabel = (score: number): string => {
    if (score >= 85) return 'High Confidence';
    if (score >= 60) return 'Medium Confidence';
    return 'Low Confidence';
  };

  const getIcon = (score: number) => {
    if (score >= 85) return <TrendingUp className="w-5 h-5 text-emerald-400" />;
    if (score >= 60) return <Minus className="w-5 h-5 text-amber-400" />;
    return <TrendingDown className="w-5 h-5 text-rose-400" />;
  };

  const radius = 70;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className="flex items-center gap-8">
      {/* Circular Gauge */}
      <div className="relative">
        <svg width="180" height="180" className="transform -rotate-90">
          {/* Background circle */}
          <circle
            cx="90"
            cy="90"
            r={radius}
            fill="none"
            stroke="currentColor"
            strokeWidth="10"
            className="text-white/5"
          />
          
          {/* Progress circle */}
          <circle
            cx="90"
            cy="90"
            r={radius}
            fill="none"
            stroke={`url(#${getGradientId(score)})`}
            strokeWidth="10"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            className="transition-all duration-1000 ease-out"
            style={{
              filter: `drop-shadow(0 0 8px ${getColor(score)}40)`
            }}
          />

          {/* Gradient definitions */}
          <defs>
            <linearGradient id="gradient-high" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#34d399" />
              <stop offset="100%" stopColor="#3b82f6" />
            </linearGradient>
            <linearGradient id="gradient-medium" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#fbbf24" />
              <stop offset="100%" stopColor="#f59e0b" />
            </linearGradient>
            <linearGradient id="gradient-low" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#f43f5e" />
              <stop offset="100%" stopColor="#dc2626" />
            </linearGradient>
          </defs>
        </svg>

        {/* Score in center */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <div className="text-4xl font-bold font-display" style={{ color: getColor(score) }}>
            {score.toFixed(1)}
          </div>
          <div className="text-xs text-secondary mt-1">/ 100</div>
        </div>
      </div>

      {/* Details */}
      <div className="flex-1 space-y-3">
        <div className="flex items-center gap-2">
          {getIcon(score)}
          <h4 className="font-semibold text-lg">{getLabel(score)}</h4>
        </div>
        
        <p className="text-sm text-secondary leading-relaxed">
          {score >= 85 
            ? "Strong evidence and verified citations support this answer."
            : score >= 60
            ? "Moderate confidence. Review citations and counter-arguments."
            : "Low confidence. Significant concerns or weak evidence detected."
          }
        </p>

        {showBreakdown && (
          <div className="mt-4 pt-4 border-t border-white/5 space-y-2">
            <div className="text-xs text-muted uppercase tracking-wider mb-2">Score Factors</div>
            <ScoreFactor label="Citation Validity" value={85} color="emerald" />
            <ScoreFactor label="Retrieval Quality" value={92} color="blue" />
            <ScoreFactor label="Counter-Arguments" value={78} color="amber" />
          </div>
        )}
      </div>
    </div>
  );
}

function ScoreFactor({ label, value, color }: { label: string; value: number; color: string }) {
  const colors: Record<string, string> = {
    emerald: 'bg-emerald-500',
    blue: 'bg-blue-500',
    amber: 'bg-amber-500',
    rose: 'bg-rose-500',
  };

  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs">
        <span className="text-secondary">{label}</span>
        <span className="text-primary font-medium">{value}%</span>
      </div>
      <div className="w-full bg-white/5 rounded-full h-1.5 overflow-hidden">
        <div
          className={`h-1.5 rounded-full transition-all duration-500 ${colors[color] || colors.blue}`}
          style={{ width: `${value}%` }}
        />
      </div>
    </div>
  );
}
