import { FlaskConical } from "lucide-react";
import { useState } from "react";
import DistillTab from "./studio/DistillTab";
import LabTab from "./studio/LabTab";
import TelemetryTab from "./studio/TelemetryTab";

type StudioTab = "lab" | "distill" | "telemetry";

const TABS: Array<{ id: StudioTab; name: string; description: string }> = [
  { id: "lab", name: "Trigger lab", description: "Score skill triggers against scenarios" },
  { id: "distill", name: "Distill", description: "Discussions and notes into skill sections" },
  { id: "telemetry", name: "Telemetry", description: "Door usage: activations and loads" },
];

const PILOT_SKILLS = [
  {
    id: "D:\\Dev\\repos\\advanced-memory-mcp\\skills\\advanced-memory\\agentic-zettelkasten",
    label: "agentic-zettelkasten (memops)",
  },
  { id: "D:\\Dev\\repos\\devices-mcp\\skills\\devices-mcp", label: "devices-mcp" },
  {
    id: "D:\\Dev\\repos\\yahboom-mcp\\.opencode\\skills\\yahboom-session-context",
    label: "yahboom-session-context",
  },
];

export default function SkillStudio() {
  const [activeTab, setActiveTab] = useState<StudioTab>("lab");
  const [skillId, setSkillId] = useState(PILOT_SKILLS[0]?.id ?? "");

  return (
    <div className="h-full min-h-0 overflow-y-auto scrollbar-thin scrollbar-thumb-white/10">
      <div className="max-w-5xl mx-auto px-6 py-8 pb-16">
        <header className="space-y-3 border-b border-white/10 pb-6">
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-amber-500/20 rounded-2xl">
              <FlaskConical className="h-6 w-6 text-amber-500" />
            </div>
            <div>
              <h1 className="text-3xl font-bold tracking-tight text-white">SkillStudio</h1>
              <p className="text-slate-400 max-w-3xl">
                Measure skill triggers, then regenerate skills from live sources. Scores first,
                rewrites second.
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3 pt-2">
            <label htmlFor="studio-skill" className="text-sm text-slate-400">
              Pilot skill
            </label>
            <select
              id="studio-skill"
              data-testid="studio-skill"
              value={skillId}
              onChange={(e) => setSkillId(e.target.value)}
              className="rounded-xl border border-white/10 bg-black/30 px-4 py-2 text-sm text-white outline-none focus:border-amber-400/50"
            >
              {PILOT_SKILLS.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.label}
                </option>
              ))}
            </select>
            <input
              value={PILOT_SKILLS.some((s) => s.id === skillId) ? "" : skillId}
              onChange={(e) => setSkillId(e.target.value)}
              placeholder="or custom skill id / path…"
              className="rounded-xl border border-white/10 bg-black/30 px-4 py-2 text-sm text-white placeholder:text-slate-600 outline-none focus:border-amber-400/50"
            />
          </div>
        </header>

        <div className="border-b border-white/10 overflow-x-auto" data-testid="studio-tabs">
          <nav className="flex space-x-6 min-w-max">
            {TABS.map((tab) => (
              <button
                key={tab.id}
                type="button"
                data-testid={`studio-tab-${tab.id}`}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors text-left ${
                  activeTab === tab.id
                    ? "border-amber-400 text-white"
                    : "border-transparent text-slate-500 hover:text-slate-200 hover:border-white/20"
                }`}
              >
                <span className="block">{tab.name}</span>
                <span className="block text-xs opacity-70 mt-0.5 font-normal">{tab.description}</span>
              </button>
            ))}
          </nav>
        </div>

        <div className="py-6">
          {activeTab === "lab" && <LabTab skillId={skillId} />}
          {activeTab === "distill" && <DistillTab skillId={skillId} />}
          {activeTab === "telemetry" && <TelemetryTab skillId={skillId} />}
        </div>
      </div>
    </div>
  );
}
