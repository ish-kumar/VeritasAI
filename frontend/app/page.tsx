/**
 * Home Page - Landing
 * 
 * Professional landing page with hero, features, and minimal footer.
 */

'use client';

import { 
  Shield, 
  CheckCircle, 
  AlertTriangle,
  TrendingUp,
  Globe,
  Target
} from 'lucide-react';
import Link from 'next/link';
import { LegalHeroSection } from '@/components/ui/legal-hero-section';
import { BentoGrid, type BentoItem } from '@/components/ui/bento-grid';
import { ScrollReveal } from '@/components/ui/scroll-reveal';

export default function HomePage() {
  const legalFeatures: BentoItem[] = [
    {
      title: "Adversarial Reasoning",
      meta: "Blue vs Red Team",
      description:
        "Every answer is challenged by a Counter-Argument Agent acting as Red Team to identify contradictions, exceptions, and edge cases before you see the result.",
      icon: <Shield className="w-4 h-4 text-blue-500" />,
      status: "Core",
      tags: ["Multi-Agent", "Validation"],
      colSpan: 2,
      hasPersistentHover: true,
    },
    {
      title: "Citation Verification",
      meta: "Fuzzy matching",
      description: "Multi-layer checks ensure every citation is grounded in actual document text with automated source validation",
      icon: <CheckCircle className="w-4 h-4 text-emerald-500" />,
      status: "Automated",
      tags: ["Source", "Grounding"],
    },
    {
      title: "Confidence Scoring",
      meta: "0-100 scale",
      description: "Composite score based on citation quality, retrieval accuracy, and counter-argument severity",
      icon: <TrendingUp className="w-4 h-4 text-blue-500" />,
      status: "Real-time",
      tags: ["Metrics", "Transparency"],
      colSpan: 2,
    },
    {
      title: "Risk Assessment",
      meta: "4-tier system",
      description: "Independent legal risk levels (low/medium/high/critical) for liability awareness",
      icon: <AlertTriangle className="w-4 h-4 text-amber-500" />,
      status: "Real-time",
      tags: ["Safety", "Compliance"],
    },
    {
      title: "Jurisdiction Detection",
      meta: "Auto-detect",
      description: "Automatically identify applicable legal jurisdictions and filter clauses accordingly",
      icon: <Globe className="w-4 h-4 text-purple-500" />,
      status: "Active",
      tags: ["Context", "Smart"],
    },
    {
      title: "Safe Refusals",
      meta: "Transparent",
      description: "System refuses low-confidence queries with full explanation of why, protecting against hallucinations",
      icon: <Target className="w-4 h-4 text-rose-500" />,
      status: "Built-in",
      tags: ["Safety", "Trust"],
    },
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section with Dithering Effect */}
      <LegalHeroSection />

      {/* Features Section with Bento Grid */}
      <section className="px-8 pt-24 pb-20 relative">
        <div className="max-w-7xl mx-auto">
          <ScrollReveal>
            <div className="text-center mb-12">
              <h2 className="text-3xl md:text-4xl font-bold mb-3">
                Built for <span className="gradient-text">Legal Precision</span>
              </h2>
              <p className="text-lg text-secondary max-w-2xl mx-auto">
                Multi-layer validation ensures every answer is grounded, verified, and transparent
              </p>
            </div>
          </ScrollReveal>

          <ScrollReveal delay={0.2}>
            <BentoGrid items={legalFeatures} />
          </ScrollReveal>
        </div>
      </section>

      {/* Footer Section */}
      <ScrollReveal delay={0.1}>
        <footer className="px-8 py-8 border-t border-white/10">
          <div className="max-w-7xl mx-auto">
            {/* Single Row Footer */}
            <div className="flex flex-col md:flex-row justify-between items-center gap-6">
              {/* Brand + Disclaimer */}
              <div className="flex flex-col items-center md:items-start gap-3 max-w-md">
                <div className="flex items-center gap-2">
                  <Shield className="w-4 h-4 text-blue-500" />
                  <span className="font-semibold text-text-primary">Veritas AI</span>
                </div>
                <p className="text-xs text-secondary leading-relaxed text-center md:text-left">
                  AI-assisted legal research. Not a substitute for professional legal advice.
                </p>
              </div>

              {/* Navigation + Copyright */}
              <div className="flex flex-col md:flex-row items-center gap-4 text-sm text-secondary">
                <Link href="/query" className="hover:text-text-primary transition-colors">Query</Link>
                <Link href="/upload" className="hover:text-text-primary transition-colors">Upload</Link>
                <Link href="/documents" className="hover:text-text-primary transition-colors">Documents</Link>
                <Link href="/history" className="hover:text-text-primary transition-colors">History</Link>
                <span className="hidden md:block text-white/10">|</span>
                <span className="text-xs">© 2026 Veritas AI</span>
              </div>
            </div>
          </div>
        </footer>
      </ScrollReveal>
    </div>
  );
}
