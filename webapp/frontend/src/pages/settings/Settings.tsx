import { useState } from "react";
import ExportSettings from "./ExportSettings";
import LLMProviderSettings from "./LLMProviderSettings";
import ResearchSettings from "./ResearchSettings";

type SettingsTab = "llm" | "research" | "export";

export default function Settings() {
  const [activeTab, setActiveTab] = useState<SettingsTab>("llm");

  const tabs = [
    { id: "llm" as const, name: "LLM Providers", description: "Configure AI models and providers" },
    { id: "research" as const, name: "Research", description: "Research sources and preferences" },
    { id: "export" as const, name: "Export", description: "Export formats and destinations" },
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Settings</h1>
          <p className="text-muted-foreground">
            Configure Advanced Memory research and AI capabilities
          </p>
        </div>
      </div>

      <div className="border-b border-border">
        <nav className="flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === tab.id
                  ? "border-accent text-accent"
                  : "border-transparent text-muted-foreground hover:text-foreground hover:border-border"
              }`}
            >
              <div className="text-left">
                <div>{tab.name}</div>
                <div className="text-xs opacity-70 mt-1">{tab.description}</div>
              </div>
            </button>
          ))}
        </nav>
      </div>

      <div className="py-6">
        {activeTab === "llm" && <LLMProviderSettings />}
        {activeTab === "research" && <ResearchSettings />}
        {activeTab === "export" && <ExportSettings />}
      </div>
    </div>
  );
}
