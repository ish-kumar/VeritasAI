import { ArrowRight } from "lucide-react"
import { useState, Suspense, lazy } from "react"
import Link from "next/link"

const Dithering = lazy(() => 
  import("@paper-design/shaders-react").then((mod) => ({ default: mod.Dithering }))
)

export function LegalHeroSection() {
  const [isHovered, setIsHovered] = useState(false)

  return (
    <section className="py-20 w-full flex justify-center items-center px-4 md:px-6">
      <div 
        className="w-full max-w-7xl relative"
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        <div className="relative overflow-hidden rounded-3xl border border-white/10 bg-surface shadow-xl min-h-[500px] md:min-h-[550px] flex flex-col items-center justify-center duration-500">
          <Suspense fallback={<div className="absolute inset-0 bg-muted/20" />}>
            <div className="absolute inset-0 z-0 pointer-events-none opacity-25 dark:opacity-15 mix-blend-multiply dark:mix-blend-screen">
              <Dithering
                colorBack="#00000000"
                colorFront="#3b82f6"
                shape="warp"
                type="4x4"
                speed={isHovered ? 0.5 : 0.15}
                className="size-full"
                minPixelRatio={1}
              />
            </div>
          </Suspense>

          <div className="relative z-10 px-6 py-12 max-w-4xl mx-auto text-center flex flex-col items-center">
            
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-blue-500/20 bg-blue-500/10 px-3 py-1 text-xs font-medium text-blue-400 backdrop-blur-sm">
              <span className="relative flex h-1.5 w-1.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-blue-400"></span>
              </span>
              Multi-Agent Legal Research
            </div>

            {/* Headline */}
            <h1 className="font-display text-5xl md:text-6xl lg:text-7xl font-bold tracking-tight text-text-primary mb-6 leading-[1.1]">
              Legal research,
              <br />
              <span className="text-text-secondary">verified & challenged.</span>
            </h1>
            
            {/* Description */}
            <p className="text-secondary text-base md:text-lg max-w-2xl mb-10 leading-relaxed">
              Adversarial multi-agent RAG that challenges every answer, verifies every citation, 
              and scores every risk. Built for accuracy and transparency.
            </p>

            {/* CTA Buttons */}
            <div className="flex gap-3 justify-center items-center flex-wrap">
              <Link 
                href="/query"
                className="group relative inline-flex h-12 items-center justify-center gap-2 overflow-hidden rounded-full bg-blue-600 px-8 text-sm font-medium text-white transition-all duration-300 hover:bg-blue-500 hover:scale-105 active:scale-95 hover:ring-4 hover:ring-blue-500/20 hover:shadow-lg hover:shadow-blue-500/50"
              >
                <span className="relative z-10">Start Researching</span>
                <ArrowRight className="h-4 w-4 relative z-10 transition-transform duration-300 group-hover:translate-x-1" />
              </Link>
              
              <Link
                href="/upload"
                className="group relative inline-flex h-12 items-center justify-center gap-2 overflow-hidden rounded-full border border-white/20 bg-white/5 px-8 text-sm font-medium text-text-primary transition-all duration-300 hover:bg-white/10 hover:border-white/30 backdrop-blur-sm"
              >
                <span className="relative z-10">Upload Documents</span>
                <ArrowRight className="h-4 w-4 relative z-10 transition-transform duration-300 group-hover:translate-x-1 opacity-50" />
              </Link>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
