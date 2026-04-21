/**
 * Counter-Argument Card Component
 * 
 * Displays the adversarial counter-argument with:
 * - Contradictions, exceptions, jurisdictional issues
 * - Ambiguities, missing context
 * - Alternative interpretations
 * - Severity level
 */

import { 
  Shield, 
  AlertTriangle, 
  AlertCircle, 
  Info,
  Scale,
  HelpCircle,
  Lightbulb
} from 'lucide-react';

interface CounterArgument {
  contradictions?: string[];
  exceptions?: string[];
  jurisdictional_issues?: string[];
  ambiguities?: string[];
  missing_context?: string[];
  alternative_interpretation?: string;
  severity: string;
}

interface CounterArgumentCardProps {
  counterArgument: CounterArgument;
}

export function CounterArgumentCard({ counterArgument }: CounterArgumentCardProps) {
  const getSeverityConfig = (severity: string) => {
    const s = severity.toLowerCase();
    if (s === 'severe' || s === 'critical') {
      return {
        color: 'border-rose-500/30 bg-rose-500/10',
        icon: <AlertCircle className="w-6 h-6 text-rose-400" />,
        label: 'Critical Severity',
        textColor: 'text-rose-400'
      };
    }
    if (s === 'high') {
      return {
        color: 'border-orange-500/30 bg-orange-500/10',
        icon: <AlertTriangle className="w-6 h-6 text-orange-400" />,
        label: 'High Severity',
        textColor: 'text-orange-400'
      };
    }
    if (s === 'moderate' || s === 'medium') {
      return {
        color: 'border-amber-500/30 bg-amber-500/10',
        icon: <Info className="w-6 h-6 text-amber-400" />,
        label: 'Moderate Severity',
        textColor: 'text-amber-400'
      };
    }
    return {
      color: 'border-blue-500/30 bg-blue-500/10',
      icon: <Shield className="w-6 h-6 text-blue-400" />,
      label: 'Low Severity',
      textColor: 'text-blue-400'
    };
  };

  const hasContent = 
    (counterArgument.contradictions && counterArgument.contradictions.length > 0) ||
    (counterArgument.exceptions && counterArgument.exceptions.length > 0) ||
    (counterArgument.jurisdictional_issues && counterArgument.jurisdictional_issues.length > 0) ||
    (counterArgument.ambiguities && counterArgument.ambiguities.length > 0) ||
    (counterArgument.missing_context && counterArgument.missing_context.length > 0) ||
    counterArgument.alternative_interpretation;

  if (!hasContent) {
    return null;
  }

  const config = getSeverityConfig(counterArgument.severity);

  return (
    <div className={`p-6 rounded-2xl border ${config.color} transition-all`}>
      {/* Header */}
      <div className="flex items-start gap-4 mb-6">
        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-rose-500/20 to-orange-500/20 flex items-center justify-center flex-shrink-0">
          {config.icon}
        </div>
        <div>
          <h4 className="text-xl font-bold mb-1">Counter-Argument Analysis</h4>
          <div className="flex items-center gap-2">
            <span className="text-sm text-secondary">Severity:</span>
            <span className={`text-sm font-semibold ${config.textColor}`}>
              {config.label}
            </span>
          </div>
        </div>
      </div>

      {/* Content Sections */}
      <div className="space-y-5">
        {counterArgument.contradictions && counterArgument.contradictions.length > 0 && (
          <Section
            icon={<AlertCircle className="w-5 h-5 text-rose-400" />}
            title="Contradictions"
            items={counterArgument.contradictions}
            color="rose"
          />
        )}

        {counterArgument.exceptions && counterArgument.exceptions.length > 0 && (
          <Section
            icon={<AlertTriangle className="w-5 h-5 text-orange-400" />}
            title="Exceptions"
            items={counterArgument.exceptions}
            color="orange"
          />
        )}

        {counterArgument.jurisdictional_issues && counterArgument.jurisdictional_issues.length > 0 && (
          <Section
            icon={<Scale className="w-5 h-5 text-amber-400" />}
            title="Jurisdictional Issues"
            items={counterArgument.jurisdictional_issues}
            color="amber"
          />
        )}

        {counterArgument.ambiguities && counterArgument.ambiguities.length > 0 && (
          <Section
            icon={<HelpCircle className="w-5 h-5 text-blue-400" />}
            title="Ambiguities"
            items={counterArgument.ambiguities}
            color="blue"
          />
        )}

        {counterArgument.missing_context && counterArgument.missing_context.length > 0 && (
          <Section
            icon={<Info className="w-5 h-5 text-purple-400" />}
            title="Missing Context"
            items={counterArgument.missing_context}
            color="purple"
          />
        )}

        {counterArgument.alternative_interpretation && (
          <div className="pt-5 border-t border-white/10">
            <div className="flex items-center gap-2 mb-3">
              <Lightbulb className="w-5 h-5 text-indigo-400" />
              <h5 className="text-sm font-semibold text-indigo-400 uppercase tracking-wider">
                Alternative Interpretation
              </h5>
            </div>
            <p className="text-sm leading-relaxed text-secondary pl-7 italic">
              {counterArgument.alternative_interpretation}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

function Section({ 
  icon, 
  title, 
  items, 
  color 
}: { 
  icon: React.ReactNode; 
  title: string; 
  items: string[]; 
  color: string;
}) {
  const colorClasses: Record<string, string> = {
    rose: 'text-rose-400',
    orange: 'text-orange-400',
    amber: 'text-amber-400',
    blue: 'text-blue-400',
    purple: 'text-purple-400',
  };

  return (
    <div>
      <div className="flex items-center gap-2 mb-3">
        {icon}
        <h5 className={`text-sm font-semibold ${colorClasses[color]} uppercase tracking-wider`}>
          {title}
        </h5>
      </div>
      <ul className="space-y-2 pl-7">
        {items.map((item, i) => (
          <li key={i} className="flex gap-2 text-sm text-secondary">
            <span className={`${colorClasses[color]} mt-0.5`}>•</span>
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
