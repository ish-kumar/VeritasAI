/**
 * Design System Test Page
 * 
 * This page demonstrates all the new design system components.
 * Navigate to /test-design to view.
 */

'use client';

import { 
  Search, 
  Upload, 
  FileText, 
  CheckCircle, 
  AlertTriangle, 
  XCircle,
  Info,
  Scale,
  Shield,
  Zap
} from 'lucide-react';

export default function TestDesignPage() {
  return (
    <div className="min-h-screen px-8 py-12">
      <div className="max-w-6xl mx-auto space-y-12">
        {/* Header */}
        <div className="text-center">
          <h1 className="mb-4">Design System Test</h1>
          <p className="text-secondary text-lg">
            Verify all components are working correctly
          </p>
          <div className="mt-4 inline-flex items-center gap-2 px-4 py-2 rounded-full glass">
            <span className="text-sm text-secondary">Fonts:</span>
            <span className="text-sm font-semibold">Plus Jakarta Sans</span>
            <span className="text-secondary">+</span>
            <span className="text-sm font-semibold font-display">Space Grotesk</span>
          </div>
        </div>

        {/* Font Showcase */}
        <section>
          <h2 className="mb-6">Typography</h2>
          <div className="space-y-8">
            {/* Space Grotesk (Headings) */}
            <div className="p-8 rounded-2xl glass">
              <div className="text-sm text-secondary mb-4 font-mono">font-display (Space Grotesk)</div>
              <h1 className="mb-4">The quick brown fox jumps</h1>
              <h2 className="mb-4">Over the lazy dog near the riverbank</h2>
              <h3 className="mb-4">Typography matters for great design</h3>
            </div>

            {/* Plus Jakarta Sans (Body) */}
            <div className="p-8 rounded-2xl glass">
              <div className="text-sm text-secondary mb-4 font-mono">font-sans (Plus Jakarta Sans)</div>
              <p className="text-2xl font-bold mb-3">The quick brown fox jumps over the lazy dog</p>
              <p className="text-xl font-semibold mb-3">Modern geometric sans-serif with personality</p>
              <p className="text-lg mb-3">Perfect for body text, UI elements, and professional content</p>
              <p className="text-base mb-3">Available in 6 weights from light to extrabold</p>
              <p className="text-sm text-secondary">Small text maintains excellent readability</p>
            </div>

            {/* Weight Scale */}
            <div className="p-8 rounded-2xl glass">
              <div className="text-sm text-secondary mb-4 font-mono">Font Weights</div>
              <div className="space-y-2">
                <p className="font-light text-xl">Light 300 - Subtle, refined text</p>
                <p className="font-normal text-xl">Normal 400 - Body text default</p>
                <p className="font-medium text-xl">Medium 500 - UI elements</p>
                <p className="font-semibold text-xl">Semibold 600 - Emphasis</p>
                <p className="font-bold text-xl">Bold 700 - Strong headings</p>
                <p className="font-extrabold text-xl">Extrabold 800 - Hero text</p>
              </div>
            </div>
          </div>
        </section>

        {/* Original Typography section removed */}
        <section>
          <h2 className="mb-6">Color Palette</h2>
          <div className="grid grid-cols-3 gap-4">
            <ColorSwatch color="bg-background" label="Background" />
            <ColorSwatch color="bg-surface" label="Surface" />
            <ColorSwatch color="bg-border" label="Border" />
            <ColorSwatch color="bg-accent-blue" label="Blue" />
            <ColorSwatch color="bg-accent-purple" label="Purple" />
            <ColorSwatch color="bg-accent-emerald" label="Emerald" />
            <ColorSwatch color="bg-accent-amber" label="Amber" />
            <ColorSwatch color="bg-accent-rose" label="Rose" />
          </div>
        </section>

        {/* Color Palette */}
        <section>
          <h2 className="mb-6">Color Palette</h2>
          <div className="grid grid-cols-3 gap-4">
            <ColorSwatch color="bg-background" label="Background" />
            <ColorSwatch color="bg-surface" label="Surface" />
            <ColorSwatch color="bg-border" label="Border" />
            <ColorSwatch color="bg-accent-blue" label="Blue" />
            <ColorSwatch color="bg-accent-purple" label="Purple" />
            <ColorSwatch color="bg-accent-emerald" label="Emerald" />
            <ColorSwatch color="bg-accent-amber" label="Amber" />
            <ColorSwatch color="bg-accent-rose" label="Rose" />
          </div>
        </section>

        {/* Icons */}
        <section>
          <h2 className="mb-6">Icons (Lucide React)</h2>
          <div className="flex gap-6 flex-wrap">
            <IconDemo icon={<Search className="w-6 h-6" />} label="Search" />
            <IconDemo icon={<Upload className="w-6 h-6" />} label="Upload" />
            <IconDemo icon={<FileText className="w-6 h-6" />} label="File" />
            <IconDemo icon={<CheckCircle className="w-6 h-6" />} label="Success" />
            <IconDemo icon={<AlertTriangle className="w-6 h-6" />} label="Warning" />
            <IconDemo icon={<XCircle className="w-6 h-6" />} label="Error" />
            <IconDemo icon={<Info className="w-6 h-6" />} label="Info" />
            <IconDemo icon={<Scale className="w-6 h-6" />} label="Legal" />
            <IconDemo icon={<Shield className="w-6 h-6" />} label="Shield" />
            <IconDemo icon={<Zap className="w-6 h-6" />} label="Speed" />
          </div>
        </section>

        {/* Cards */}
        <section>
          <h2 className="mb-6">Card Styles</h2>
          <div className="grid md:grid-cols-3 gap-6">
            {/* Glassmorphism Card */}
            <div className="glass p-6 rounded-2xl">
              <h4 className="mb-2">Glassmorphism</h4>
              <p className="text-sm text-secondary">
                Subtle blur effect with transparency
              </p>
            </div>

            {/* Card with hover */}
            <div className="card-hover p-6 rounded-2xl border border-white/10 bg-surface">
              <h4 className="mb-2">Hover Effect</h4>
              <p className="text-sm text-secondary">
                Lifts on hover with shadow
              </p>
            </div>

            {/* Gradient card */}
            <div className="p-6 rounded-2xl bg-gradient-to-br from-blue-500/10 to-purple-500/10 border border-white/10">
              <h4 className="mb-2">Gradient Background</h4>
              <p className="text-sm text-secondary">
                Subtle color gradient
              </p>
            </div>
          </div>
        </section>

        {/* Buttons */}
        <section>
          <h2 className="mb-6">Buttons</h2>
          <div className="flex gap-4 flex-wrap">
            <button className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl font-semibold hover:shadow-lg hover:shadow-blue-500/25 transform hover:-translate-y-0.5 transition-all button-press">
              Primary Button
            </button>
            <button className="px-6 py-3 border border-white/10 rounded-xl font-semibold hover:bg-white/5 transition-all button-press">
              Secondary Button
            </button>
            <button className="px-6 py-3 bg-accent-emerald/10 border border-accent-emerald/20 text-accent-emerald rounded-xl font-semibold hover:bg-accent-emerald/20 transition-all button-press">
              Success Button
            </button>
            <button className="px-6 py-3 bg-accent-rose/10 border border-accent-rose/20 text-accent-rose rounded-xl font-semibold hover:bg-accent-rose/20 transition-all button-press">
              Danger Button
            </button>
          </div>
        </section>

        {/* Gradient Text */}
        <section>
          <h2 className="mb-6">Text Effects</h2>
          <div className="space-y-4">
            <p className="text-4xl font-bold gradient-text">
              Gradient Text Effect
            </p>
            <p className="text-2xl font-semibold bg-gradient-to-r from-emerald-400 to-blue-500 bg-clip-text text-transparent">
              Custom Gradient Text
            </p>
          </div>
        </section>

        {/* Icon Containers */}
        <section>
          <h2 className="mb-6">Icon Containers</h2>
          <div className="flex gap-6">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 flex items-center justify-center">
              <Scale className="w-8 h-8 text-blue-400" />
            </div>
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-emerald-500/20 to-blue-500/20 flex items-center justify-center">
              <CheckCircle className="w-8 h-8 text-emerald-400" />
            </div>
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-amber-500/20 to-rose-500/20 flex items-center justify-center">
              <AlertTriangle className="w-8 h-8 text-amber-400" />
            </div>
          </div>
        </section>

        {/* Animations */}
        <section>
          <h2 className="mb-6">Animations</h2>
          <div className="flex gap-6">
            <div className="w-24 h-24 rounded-2xl gradient-bg-animated flex items-center justify-center">
              <Zap className="w-12 h-12 text-accent-blue" />
            </div>
            <div className="w-24 h-24 rounded-full border-4 border-transparent border-t-blue-500 border-r-purple-500 animate-spin" />
            <div className="w-24 h-24 rounded-2xl bg-accent-purple/10 animate-pulse flex items-center justify-center">
              <Shield className="w-12 h-12 text-accent-purple" />
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

function ColorSwatch({ color, label }: { color: string; label: string }) {
  return (
    <div>
      <div className={`${color} h-20 rounded-xl border border-white/10 mb-2`} />
      <p className="text-sm text-center text-secondary">{label}</p>
    </div>
  );
}

function IconDemo({ icon, label }: { icon: React.ReactNode; label: string }) {
  return (
    <div className="flex flex-col items-center gap-2">
      <div className="w-12 h-12 rounded-lg glass flex items-center justify-center text-blue-400">
        {icon}
      </div>
      <span className="text-xs text-secondary">{label}</span>
    </div>
  );
}
