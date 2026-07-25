import { Layers, Wrench } from "lucide-react";
import { Link } from "react-router-dom";

export default function SkillStudio() {
  return (
    <div className="flex flex-col h-full bg-background overflow-hidden">
      <div className="px-12 py-10 border-b border-white/5 bg-black/20">
        <div className="max-w-5xl mx-auto">
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-amber-500/20 rounded-2xl">
              <Layers className="h-6 w-6 text-amber-500" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight">Skill Synthesis Studio</h1>
              <p className="text-xs text-muted-foreground uppercase tracking-widest font-bold">
                Skill authoring
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="flex-1 flex items-center justify-center">
        <div className="text-center opacity-40 max-w-md">
          <Wrench className="h-12 w-12 mx-auto mb-4" />
          <h3 className="text-lg font-bold mb-2">Not Yet Available</h3>
          <p className="text-sm text-muted-foreground mb-4">
            The Skill Studio requires a backend synthesis API that has not been
            connected yet. Use the <Link to="/skills" className="text-amber-400 hover:underline">Skills page</Link> to browse existing skills,
            or create skills via the MCP tools.
          </p>
        </div>
      </div>
    </div>
  );
}
