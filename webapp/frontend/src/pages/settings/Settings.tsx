import { AlertCircle, CheckCircle, RefreshCw, Save } from "lucide-react";
import { useState } from "react";
import ExportSettings from "./ExportSettings";
import LLMProviderSettings from "./LLMProviderSettings";
import ResearchSettings from "./ResearchSettings";

type SettingsTab = "llm" | "research" | "export";

export default function Settings() {
  const [activeTab, setActiveTab] = useState<SettingsTab>("llm");
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState<"idle" | "success" | "error">("idle");

  const handleSave = async () => {
    setIsSaving(true);
    setSaveStatus("idle");

    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000));

      setSaveStatus("success");
      setHasUnsavedChanges(false);

      setTimeout(() => setSaveStatus("idle"), 3000);
    } catch (error) {
      setSaveStatus("error");
      setTimeout(() => setSaveStatus("idle"), 3000);
    } finally {
      setIsSaving(false);
    }
  };

  const tabs = [
    { id: "llm" as const, name: "LLM Providers", description: "Configure AI models and providers" },
    { id: "research" as const, name: "Research", description: "Research sources and preferences" },
    { id: "export" as const, name: "Export", description: "Export formats and destinations" },
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Settings</h1>
          <p className="text-muted-foreground">
            Configure Advanced Memory research and AI capabilities
          </p>
        </div>

        {hasUnsavedChanges && (
          <div className="flex items-center space-x-3">
            <span className="text-sm text-muted-foreground">Unsaved changes</span>
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="btn btn-primary flex items-center"
            >
              {isSaving ? (
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Save className="h-4 w-4 mr-2" />
              )}
              {isSaving ? "Saving..." : "Save Changes"}
            </button>
          </div>
        )}
      </div>

      {/* Save status */}
      {saveStatus !== "idle" && (
        <div
          className={`flex items-center p-4 rounded-md ${
            saveStatus === "success"
              ? "bg-green-500/10 border border-green-500/20 text-green-400"
              : "bg-red-500/10 border border-red-500/20 text-red-400"
          }`}
        >
          {saveStatus === "success" ? (
            <CheckCircle className="h-5 w-5 mr-3" />
          ) : (
            <AlertCircle className="h-5 w-5 mr-3" />
          )}
          {saveStatus === "success" ? "Settings saved successfully" : "Failed to save settings"}
        </div>
      )}

      {/* Tabs */}
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

      {/* Tab content */}
      <div className="py-6">
        {activeTab === "llm" && <LLMProviderSettings onChange={() => setHasUnsavedChanges(true)} />}
        {activeTab === "research" && (
          <ResearchSettings onChange={() => setHasUnsavedChanges(true)} />
        )}
        {activeTab === "export" && <ExportSettings onChange={() => setHasUnsavedChanges(true)} />}
      </div>
    </div>
  );
}
