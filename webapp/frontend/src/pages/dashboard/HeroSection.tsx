import { ArrowRight, Sparkles } from "lucide-react";

export default function HeroSection() {
  return (
    <div className="relative overflow-hidden rounded-lg border border-accent bg-gradient-to-br from-background to-background/80">
      {/* Background decoration */}
      <div className="absolute inset-0 bg-gradient-to-r from-accent/5 via-transparent to-accent/5" />

      <div className="relative p-8 lg:p-12">
        <div className="max-w-4xl mx-auto text-center">
          {/* Main heading */}
          <div className="flex items-center justify-center mb-6">
            <Sparkles className="h-8 w-8 text-accent mr-3" />
            <h1 className="text-4xl lg:text-6xl font-bold bg-gradient-to-r from-foreground via-foreground to-accent bg-clip-text text-transparent">
              Advanced Memory
            </h1>
            <Sparkles className="h-8 w-8 text-accent ml-3" />
          </div>

          {/* Subtitle */}
          <p className="text-xl lg:text-2xl text-muted-foreground mb-8 max-w-3xl mx-auto leading-relaxed">
            Transform any AI assistant into a research powerhouse with multi-source intelligence,
            academic literature access, code analysis, and intelligent skill creation.
          </p>

          {/* Key features */}
          <div className="grid gap-6 md:grid-cols-3 mb-10">
            <div className="text-center">
              <div className="text-2xl font-bold text-accent mb-2">15+</div>
              <div className="text-sm text-muted-foreground">Research Sources</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-accent mb-2">FastMCP</div>
              <div className="text-sm text-muted-foreground">2.14.3 Compatible</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-accent mb-2">Zero Crash</div>
              <div className="text-sm text-muted-foreground">Bulletproof Design</div>
            </div>
          </div>

          {/* CTA buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <button className="btn btn-primary btn-lg group">
              Start Research
              <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
            </button>

            <button className="btn btn-outline btn-lg">View Documentation</button>
          </div>

          {/* Status indicator */}
          <div className="mt-8 flex items-center justify-center">
            <div className="flex items-center px-4 py-2 bg-green-500/10 border border-green-500/20 rounded-full">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-3 animate-pulse"></div>
              <span className="text-sm font-medium text-green-400">
                System Online - All Research Services Available
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Decorative elements */}
      <div className="absolute top-4 right-4 opacity-10">
        <Sparkles className="h-16 w-16 text-accent" />
      </div>
      <div className="absolute bottom-4 left-4 opacity-10">
        <Sparkles className="h-12 w-12 text-accent" />
      </div>
    </div>
  );
}
