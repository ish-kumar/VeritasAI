/**
 * Risk Badge Component
 * 
 * Color-coded badge showing legal risk level.
 * Independent of confidence score.
 */

import { CheckCircle, AlertTriangle, AlertCircle, ShieldAlert } from 'lucide-react';

interface RiskBadgeProps {
  level: string;
  size?: 'sm' | 'md' | 'lg';
}

export function RiskBadge({ level, size = 'md' }: RiskBadgeProps) {
  const normalizedLevel = level.toLowerCase();
  
  const config: Record<string, { 
    color: string; 
    bgColor: string;
    icon: React.ReactNode; 
    label: string;
    glowColor: string;
  }> = {
    low: { 
      color: 'text-emerald-400',
      bgColor: 'bg-emerald-500/10 border-emerald-500/20',
      icon: <CheckCircle className="w-4 h-4" />,
      label: 'Low Risk',
      glowColor: 'hover:shadow-emerald-500/20'
    },
    medium: { 
      color: 'text-amber-400',
      bgColor: 'bg-amber-500/10 border-amber-500/20',
      icon: <AlertTriangle className="w-4 h-4" />,
      label: 'Medium Risk',
      glowColor: 'hover:shadow-amber-500/20'
    },
    high: { 
      color: 'text-orange-400',
      bgColor: 'bg-orange-500/10 border-orange-500/20',
      icon: <AlertCircle className="w-4 h-4" />,
      label: 'High Risk',
      glowColor: 'hover:shadow-orange-500/20'
    },
    critical: { 
      color: 'text-rose-400',
      bgColor: 'bg-rose-500/10 border-rose-500/20',
      icon: <ShieldAlert className="w-4 h-4" />,
      label: 'Critical Risk',
      glowColor: 'hover:shadow-rose-500/20'
    },
  };

  const { color, bgColor, icon, label, glowColor } = config[normalizedLevel] || config.medium;

  const sizeClasses = {
    sm: 'px-2.5 py-1 text-xs',
    md: 'px-3 py-1.5 text-sm',
    lg: 'px-4 py-2 text-base',
  };

  return (
    <span className={`
      inline-flex items-center gap-2 rounded-full font-semibold border
      ${color} ${bgColor} ${sizeClasses[size]} ${glowColor}
      transition-all duration-200 hover:shadow-lg
    `}>
      {icon}
      <span>{label}</span>
    </span>
  );
}
