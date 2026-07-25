import { ArrowRight, Sparkles } from "lucide-react";
import { Link } from "react-router-dom";

export default function HeroSection() {
  return (
    <div className="relative overflow-hidden rounded-lg border border-accent bg-gradient-to-br from-background to-background/80">
      <div className="absolute inset-0 bg-gradient-to-r from-accent/5 via-transparent to-accent/5" />

      <div className="relative p-8 lg:p-12">
        <div className="max-w-4xl mx-auto text-center">
          <div className="flex items-center justify-center mb-6">
            <Sparkles className="h-8 w-8 text-accent mr-3" />
            <h1 className="text-4xl lg:text-6xl font-bold bg-gradient-to-r from-foreground via-foreground to-accent bg-clip-text text-transparent">
              Advanced Memory
            </h1>
            <Sparkles className="h-8 w-8 text-accent ml-3" />
          </div>

          <p className="text-xl lg:text-2xl text-muted-foreground mb-8 max-w-3xl mx-auto leading-relaxed">
            Transform any AI assistant into a research powerhouse with multi-source intelligence,
            academic literature access, code analysis, and intelligent skill creation.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Link to="/notes" className="btn btn-primary btn-lg group">
              Browse Notes
              <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link to="/skills" className="btn btn-outline btn-lg">
              View Skills
            </Link>
            <Link to="/research" className="btn btn-outline btn-lg">
              Research Lab
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
