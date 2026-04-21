import {
  AlertCircle,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Copy,
  FileText,
  Layers,
  Loader2,
  Save,
  Sparkles,
  Tag,
  Target,
  Wand2,
} from "lucide-react";
import { useState } from "react";
import { apiService } from "../../services/api";

type CreatorMode = "guided" | "advanced";

interface GeneratedSkill {
  name: string;
  content: string;
  tags: string[];
  type: string;
  metadata?: Record<string, any>;
}

export default function SkillCreator() {
  // Guided mode state
  const [description, setDescription] = useState("");
  const [targetTags, setTargetTags] = useState("");
  const [skillType, setSkillType] = useState("general");

  // Advanced mode state
  const [advancedName, setAdvancedName] = useState("");
  const [advancedContent, setAdvancedContent] = useState("");
  const [advancedTags, setAdvancedTags] = useState("");
  const [advancedParams, setAdvancedParams] = useState("{}");
  const [showAdvancedParams, setShowAdvancedParams] = useState(false);

  // Common state
  const [creatorMode, setCreatorMode] = useState<CreatorMode>("guided");
  const [status, setStatus] = useState<"idle" | "generating" | "success" | "error">("idle");
  const [statusMessage, setStatusMessage] = useState("");
  const [generatedSkill, setGeneratedSkill] = useState<GeneratedSkill | null>(null);
  const [savedSuccessfully, setSavedSuccessfully] = useState(false);

  const skillTypes = [
    { id: "general", label: "General", description: "Broad knowledge skill" },
    { id: "technical", label: "Technical", description: "Programming or engineering" },
    { id: "creative", label: "Creative", description: "Writing, art, or design" },
    { id: "research", label: "Research", description: "Academic or scientific" },
    { id: "workflow", label: "Workflow", description: "Process automation" },
    { id: "analysis", label: "Analysis", description: "Data or system analysis" },
  ];

  const handleGuidedGenerate = async () => {
    if (!description.trim()) {
      setStatus("error");
      setStatusMessage("Please describe the skill you want to create");
      return;
    }

    setStatus("generating");
    setStatusMessage("AI is crafting your skill...");
    setGeneratedSkill(null);
    setSavedSuccessfully(false);

    try {
      const response = await apiService.callMCPTool("adn_skills", {
        operation: "creator",
        content: description.trim(),
        tags: targetTags
          .split(",")
          .map((t) => t.trim())
          .filter(Boolean),
        skill_type: skillType,
      });

      if (response.success && response.data) {
        const data = response.data.result || response.data;
        setGeneratedSkill({
          name: data.name || data.title || "Generated Skill",
          content: data.content || data.skill_content || JSON.stringify(data, null, 2),
          tags: data.tags || [],
          type: data.type || skillType,
          metadata: data.metadata,
        });
        setStatus("success");
        setStatusMessage("Skill generated successfully!");
      } else {
        setStatus("error");
        setStatusMessage(response.error || "Generation failed");
      }
    } catch (error: any) {
      setStatus("error");
      setStatusMessage(error.message || "Failed to generate skill");
    }
  };

  const handleAdvancedCreate = async () => {
    if (!advancedName.trim()) {
      setStatus("error");
      setStatusMessage("Skill name is required");
      return;
    }

    setStatus("generating");
    setStatusMessage("Creating advanced skill...");
    setGeneratedSkill(null);
    setSavedSuccessfully(false);

    try {
      let params = {};
      try {
        params = JSON.parse(advancedParams);
      } catch {
        // ignore parse errors, use empty params
      }

      const response = await apiService.callMCPTool("adn_skills", {
        operation: "advanced_create",
        name: advancedName.trim(),
        content: advancedContent.trim() || undefined,
        tags: advancedTags
          .split(",")
          .map((t) => t.trim())
          .filter(Boolean),
        parameters: Object.keys(params).length > 0 ? params : undefined,
      });

      if (response.success && response.data) {
        const data = response.data.result || response.data;
        setGeneratedSkill({
          name: data.name || advancedName,
          content: data.content || advancedContent || JSON.stringify(data, null, 2),
          tags:
            data.tags ||
            advancedTags
              .split(",")
              .map((t) => t.trim())
              .filter(Boolean),
          type: data.type || "advanced",
          metadata: data.metadata,
        });
        setStatus("success");
        setStatusMessage("Advanced skill created!");
      } else {
        setStatus("error");
        setStatusMessage(response.error || "Creation failed");
      }
    } catch (error: any) {
      setStatus("error");
      setStatusMessage(error.message || "Failed to create skill");
    }
  };

  const handleSaveSkill = async () => {
    if (!generatedSkill) return;

    try {
      const response = await apiService.callMCPTool("adn_skills", {
        operation: "create",
        name: generatedSkill.name,
        content: generatedSkill.content,
        tags: generatedSkill.tags,
        skill_type: generatedSkill.type,
      });

      if (response.success) {
        setSavedSuccessfully(true);
        setStatusMessage("Skill saved to your knowledge base!");
      } else {
        setStatusMessage("Failed to save: " + (response.error || "Unknown error"));
      }
    } catch (error: any) {
      setStatusMessage("Save failed: " + (error.message || "Unknown error"));
    }
  };

  const copyToClipboard = () => {
    if (generatedSkill) {
      navigator.clipboard.writeText(generatedSkill.content);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold flex items-center">
          <Wand2 className="h-6 w-6 mr-2 text-accent" />
          Skill Creator
        </h1>
        <p className="text-muted-foreground">
          Generate and craft AI skills using guided or advanced creation tools
        </p>
      </div>

      {/* Mode Selector */}
      <div className="flex space-x-1 bg-muted p-1 rounded-lg w-fit">
        <button
          onClick={() => {
            setCreatorMode("guided");
            setStatus("idle");
            setGeneratedSkill(null);
          }}
          className={`flex items-center px-4 py-2 text-sm font-medium rounded-md transition-colors ${
            creatorMode === "guided"
              ? "bg-background text-foreground shadow-sm"
              : "text-muted-foreground hover:text-foreground"
          }`}
        >
          <Sparkles className="mr-2 h-4 w-4" />
          AI-Guided
        </button>
        <button
          onClick={() => {
            setCreatorMode("advanced");
            setStatus("idle");
            setGeneratedSkill(null);
          }}
          className={`flex items-center px-4 py-2 text-sm font-medium rounded-md transition-colors ${
            creatorMode === "advanced"
              ? "bg-background text-foreground shadow-sm"
              : "text-muted-foreground hover:text-foreground"
          }`}
        >
          <Layers className="mr-2 h-4 w-4" />
          Advanced
        </button>
      </div>

      {/* Guided Mode */}
      {creatorMode === "guided" && (
        <div className="space-y-5">
          <div className="bg-card border border-border rounded-lg p-5 space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2 flex items-center">
                <Target className="h-4 w-4 mr-2 text-muted-foreground" />
                Describe Your Skill
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="e.g., I need a skill for analyzing Python code quality, detecting anti-patterns, and suggesting refactoring improvements..."
                rows={4}
                className="w-full px-3 py-2 bg-background border border-border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-accent resize-none"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2 flex items-center">
                  <FileText className="h-4 w-4 mr-2 text-muted-foreground" />
                  Skill Type
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {skillTypes.map((st) => (
                    <button
                      key={st.id}
                      onClick={() => setSkillType(st.id)}
                      className={`p-2 rounded-md border text-left text-xs transition-all ${
                        skillType === st.id
                          ? "border-accent bg-accent/10"
                          : "border-border hover:border-muted-foreground/50"
                      }`}
                    >
                      <div className="font-medium">{st.label}</div>
                      <div className="text-muted-foreground mt-0.5">{st.description}</div>
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2 flex items-center">
                  <Tag className="h-4 w-4 mr-2 text-muted-foreground" />
                  Tags (comma-separated)
                </label>
                <input
                  type="text"
                  value={targetTags}
                  onChange={(e) => setTargetTags(e.target.value)}
                  placeholder="python, code-quality, refactoring"
                  className="w-full px-3 py-2 bg-background border border-border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-accent"
                />
              </div>
            </div>

            <button
              onClick={handleGuidedGenerate}
              disabled={status === "generating"}
              className="w-full px-4 py-3 bg-accent text-accent-foreground rounded-md text-sm font-medium hover:bg-accent/90 transition-colors disabled:opacity-50 flex items-center justify-center"
            >
              {status === "generating" ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Sparkles className="h-4 w-4 mr-2" />
              )}
              Generate Skill
            </button>
          </div>
        </div>
      )}

      {/* Advanced Mode */}
      {creatorMode === "advanced" && (
        <div className="space-y-5">
          <div className="bg-card border border-border rounded-lg p-5 space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Skill Name</label>
              <input
                type="text"
                value={advancedName}
                onChange={(e) => setAdvancedName(e.target.value)}
                placeholder="My Custom Skill"
                className="w-full px-3 py-2 bg-background border border-border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-accent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Skill Content (Markdown)</label>
              <textarea
                value={advancedContent}
                onChange={(e) => setAdvancedContent(e.target.value)}
                placeholder="# My Skill&#10;&#10;## Overview&#10;Detailed skill instructions..."
                rows={10}
                className="w-full px-3 py-2 bg-background border border-border rounded-md text-sm font-mono focus:outline-none focus:ring-2 focus:ring-accent resize-none"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2 flex items-center">
                <Tag className="h-4 w-4 mr-2 text-muted-foreground" />
                Tags
              </label>
              <input
                type="text"
                value={advancedTags}
                onChange={(e) => setAdvancedTags(e.target.value)}
                placeholder="tag1, tag2, tag3"
                className="w-full px-3 py-2 bg-background border border-border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-accent"
              />
            </div>

            {/* Advanced Parameters */}
            <div>
              <button
                onClick={() => setShowAdvancedParams(!showAdvancedParams)}
                className="flex items-center text-sm text-muted-foreground hover:text-foreground transition-colors"
              >
                {showAdvancedParams ? (
                  <ChevronUp className="h-4 w-4 mr-1" />
                ) : (
                  <ChevronDown className="h-4 w-4 mr-1" />
                )}
                Advanced Parameters (JSON)
              </button>
              {showAdvancedParams && (
                <textarea
                  value={advancedParams}
                  onChange={(e) => setAdvancedParams(e.target.value)}
                  rows={4}
                  className="mt-2 w-full px-3 py-2 bg-background border border-border rounded-md text-xs font-mono focus:outline-none focus:ring-2 focus:ring-accent resize-none"
                  placeholder='{"complexity": "high", "format": "anthropic"}'
                />
              )}
            </div>

            <button
              onClick={handleAdvancedCreate}
              disabled={status === "generating"}
              className="w-full px-4 py-3 bg-accent text-accent-foreground rounded-md text-sm font-medium hover:bg-accent/90 transition-colors disabled:opacity-50 flex items-center justify-center"
            >
              {status === "generating" ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Layers className="h-4 w-4 mr-2" />
              )}
              Create Advanced Skill
            </button>
          </div>
        </div>
      )}

      {/* Status / Result */}
      {status !== "idle" && !generatedSkill && (
        <div
          className={`flex items-center p-4 rounded-lg border ${
            status === "generating"
              ? "border-blue-500/30 bg-blue-500/5"
              : status === "error"
                ? "border-red-500/30 bg-red-500/5"
                : ""
          }`}
        >
          {status === "generating" && (
            <Loader2 className="h-5 w-5 mr-3 text-blue-400 animate-spin" />
          )}
          {status === "error" && <AlertCircle className="h-5 w-5 mr-3 text-red-400" />}
          <span className="text-sm">{statusMessage}</span>
        </div>
      )}

      {/* Generated Skill Preview */}
      {generatedSkill && (
        <div className="bg-card border border-border rounded-lg overflow-hidden">
          <div className="flex items-center justify-between p-4 border-b border-border">
            <div className="flex items-center">
              <CheckCircle2 className="h-5 w-5 mr-2 text-green-400" />
              <h3 className="font-semibold">{generatedSkill.name}</h3>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={copyToClipboard}
                className="p-2 rounded-md text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
                title="Copy to clipboard"
              >
                <Copy className="h-4 w-4" />
              </button>
              {!savedSuccessfully && (
                <button
                  onClick={handleSaveSkill}
                  className="px-3 py-1.5 bg-accent text-accent-foreground rounded-md text-sm font-medium hover:bg-accent/90 transition-colors flex items-center"
                >
                  <Save className="h-4 w-4 mr-1.5" />
                  Save to Knowledge Base
                </button>
              )}
              {savedSuccessfully && (
                <span className="px-3 py-1.5 text-sm text-green-400 flex items-center">
                  <CheckCircle2 className="h-4 w-4 mr-1.5" />
                  Saved
                </span>
              )}
            </div>
          </div>

          {/* Tags */}
          {generatedSkill.tags.length > 0 && (
            <div className="px-4 py-2 border-b border-border flex items-center flex-wrap gap-1.5">
              {generatedSkill.tags.map((tag, i) => (
                <span
                  key={i}
                  className="px-2 py-0.5 bg-muted rounded-full text-xs text-muted-foreground"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}

          {/* Content */}
          <pre className="p-4 text-sm font-mono whitespace-pre-wrap overflow-x-auto max-h-96 text-muted-foreground">
            {generatedSkill.content}
          </pre>
        </div>
      )}
    </div>
  );
}
