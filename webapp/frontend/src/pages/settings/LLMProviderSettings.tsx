import { AlertTriangle, CheckCircle, Play, RefreshCw, Square, XCircle } from "lucide-react";
import { useEffect, useState } from "react";

import { getApiBaseUrl } from "../../config/apiBase";

interface Provider {
  name: string;
  type: "local" | "hosted";
  status: "available" | "unavailable" | "configured" | "not_configured";
  url: string;
  description: string;
  models?: string[];
}

interface LLMProviderSettingsProps {
  onChange: () => void;
}

export default function LLMProviderSettings({ onChange }: LLMProviderSettingsProps) {
  const [providers, setProviders] = useState<Provider[]>([
    {
      name: "ollama",
      type: "local",
      status: "not_configured",
      url: "http://localhost:11434",
      description: "Local models via Ollama",
      models: [],
    },
    {
      name: "lmstudio",
      type: "local",
      status: "not_configured",
      url: "http://localhost:1234",
      description: "Local models via LM Studio (OpenAI-compatible)",
      models: [],
    },
    {
      name: "openai",
      type: "hosted",
      status: "not_configured",
      url: "https://api.openai.com/v1",
      description: "Hosted models via OpenAI API",
      models: [],
    },
  ]);

  const [selectedProvider, setSelectedProvider] = useState<string>("ollama");
  const [selectedModel, setSelectedModel] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);
  const [lastAction, setLastAction] = useState<string>("");

  const currentProvider = providers.find((p) => p.name === selectedProvider);

  // Auto-refresh providers on component mount + load persisted selection from backend
  useEffect(() => {
    handleRefreshProviders();
    (async () => {
      try {
        const r = await fetch(`${getApiBaseUrl()}/management/llm-config`);
        if (r.ok) {
          const cfg = await r.json();
          if (cfg.provider) setSelectedProvider(cfg.provider);
          if (cfg.model) setSelectedModel(cfg.model);
        }
      } catch {
        // backend offline - keep local defaults, selection just won't persist
      }
    })();
  }, []);

  // Persist provider/model selection to backend config.json (used by adn_llm + LLMClient)
  const persistSelection = async (provider: string, model: string) => {
    try {
      const r = await fetch(`${getApiBaseUrl()}/management/llm-config`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ provider, model }),
      });
      if (r.ok) {
        setLastAction(`Saved default: ${provider} / ${model || "(none)"}`);
        setTimeout(() => setLastAction(""), 3000);
      } else {
        setLastAction("Backend rejected selection - not persisted");
        setTimeout(() => setLastAction(""), 3000);
      }
    } catch {
      setLastAction("Backend offline - selection not persisted");
      setTimeout(() => setLastAction(""), 3000);
    }
  };

  // Query Ollama API for available models
  const queryOllamaModels = async (url: string): Promise<string[]> => {
    try {
      const response = await fetch(`${url}/api/tags`);
      if (!response.ok) throw new Error("Failed to fetch Ollama models");

      const data = await response.json();
      return data.models?.map((model: any) => model.name) || [];
    } catch (error) {
      console.error("Failed to query Ollama:", error);
      return [];
    }
  };

  // Query LM Studio API for available models (OpenAI-compatible)
  const queryLMStudioModels = async (url: string): Promise<string[]> => {
    try {
      const response = await fetch(`${url}/v1/models`);
      if (!response.ok) throw new Error("Failed to fetch LM Studio models");

      const data = await response.json();
      return data.data?.map((model: any) => model.id) || [];
    } catch (error) {
      console.error("Failed to query LM Studio:", error);
      return [];
    }
  };

  // Query OpenAI API for available models
  const queryOpenAIModels = async (url: string, apiKey?: string): Promise<string[]> => {
    try {
      const headers: Record<string, string> = {
        "Content-Type": "application/json",
      };
      if (apiKey) {
        headers["Authorization"] = `Bearer ${apiKey}`;
      }

      const response = await fetch(`${url}/models`, { headers });
      if (!response.ok) throw new Error("Failed to fetch OpenAI models");

      const data = await response.json();
      return data.data?.map((model: any) => model.id) || [];
    } catch (error) {
      console.error("Failed to query OpenAI:", error);
      return [];
    }
  };

  const handleRefreshProviders = async () => {
    setIsLoading(true);
    setLastAction("Refreshing provider status...");

    try {
      const updatedProviders = await Promise.all(
        providers.map(async (provider) => {
          let models: string[] = [];
          let status: Provider["status"] = "not_configured";

          if (provider.type === "local") {
            if (provider.name === "ollama") {
              models = await queryOllamaModels(provider.url);
              status = models.length > 0 ? "available" : "unavailable";
            } else if (provider.name === "lmstudio") {
              models = await queryLMStudioModels(provider.url);
              status = models.length > 0 ? "available" : "unavailable";
            }
          } else if (provider.type === "hosted") {
            // For hosted providers, try to fetch models (will fail without API key, but we can detect availability)
            try {
              models = await queryOpenAIModels(provider.url);
              status = models.length > 0 ? "configured" : "not_configured";
            } catch {
              status = "not_configured";
            }
          }

          return {
            ...provider,
            status,
            models,
          };
        }),
      );

      setProviders(updatedProviders);
      setLastAction("Provider status refreshed");
      setTimeout(() => setLastAction(""), 3000);
    } catch (error) {
      setLastAction("Failed to refresh providers");
      setTimeout(() => setLastAction(""), 3000);
    } finally {
      setIsLoading(false);
    }
  };

  // Real load/unload via Ollama keep_alive (was a fake setTimeout stub until 2026-07-17).
  // Only Ollama exposes load/unload semantics; other providers report unsupported.
  const handleLoadModel = async () => {
    setIsLoading(true);
    setLastAction(`Loading ${selectedModel}...`);

    try {
      if (selectedProvider !== "ollama") {
        throw new Error(`load/unload not supported for ${selectedProvider}`);
      }
      const url = providers.find((p) => p.name === "ollama")?.url ?? "http://localhost:11434";
      const r = await fetch(`${url}/api/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ model: selectedModel, prompt: "", keep_alive: "30m" }),
      });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      setLastAction(`Loaded ${selectedModel} (keep_alive 30m)`);
      setTimeout(() => setLastAction(""), 3000);
      onChange();
    } catch (error) {
      setLastAction(`Failed to load ${selectedModel}: ${error}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUnloadModel = async () => {
    setIsLoading(true);
    setLastAction(`Unloading ${selectedModel}...`);

    try {
      if (selectedProvider !== "ollama") {
        throw new Error(`load/unload not supported for ${selectedProvider}`);
      }
      const url = providers.find((p) => p.name === "ollama")?.url ?? "http://localhost:11434";
      const r = await fetch(`${url}/api/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ model: selectedModel, prompt: "", keep_alive: 0 }),
      });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      setLastAction(`Unloaded ${selectedModel}`);
      setTimeout(() => setLastAction(""), 3000);
      onChange();
    } catch (error) {
      setLastAction(`Failed to unload ${selectedModel}: ${error}`);
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "available":
      case "configured":
        return "text-green-400";
      case "unavailable":
        return "text-red-400";
      case "not_configured":
        return "text-yellow-400";
      default:
        return "text-gray-400";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "available":
      case "configured":
        return <CheckCircle className="h-4 w-4" />;
      case "unavailable":
        return <XCircle className="h-4 w-4" />;
      case "not_configured":
        return <AlertTriangle className="h-4 w-4" />;
      default:
        return <AlertTriangle className="h-4 w-4" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Current Configuration */}
      <div className="card p-6">
        <h2 className="text-lg font-semibold mb-4">Current LLM Configuration</h2>

        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <label className="label">Active Provider</label>
            <select
              value={selectedProvider}
              onChange={(e) => {
                setSelectedProvider(e.target.value);
                setSelectedModel("");
                onChange();
              }}
              className="input w-full"
            >
              {providers.map((provider) => (
                <option key={provider.name} value={provider.name}>
                  {provider.name} ({provider.type})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="label">Active Model</label>
            <select
              value={selectedModel}
              onChange={(e) => {
                setSelectedModel(e.target.value);
                persistSelection(selectedProvider, e.target.value);
                onChange();
              }}
              className="input w-full"
              disabled={!currentProvider?.models?.length}
            >
              <option value="">Select a model...</option>
              {currentProvider?.models?.map((model) => (
                <option key={model} value={model}>
                  {model}
                </option>
              ))}
            </select>
          </div>
        </div>

        {lastAction && (
          <div className="mt-4 p-3 bg-muted/50 rounded-md">
            <div className="flex items-center text-sm">
              {isLoading && <RefreshCw className="h-4 w-4 mr-2 animate-spin" />}
              {lastAction}
            </div>
          </div>
        )}
      </div>

      {/* Provider Status */}
      <div className="card p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold">Provider Status</h2>
          <button
            onClick={handleRefreshProviders}
            disabled={isLoading}
            className="btn btn-outline btn-sm"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? "animate-spin" : ""}`} />
            Refresh
          </button>
        </div>

        <div className="grid gap-4">
          {providers.map((provider) => (
            <div
              key={provider.name}
              className="flex items-center justify-between p-4 border border-border rounded-md"
            >
              <div className="flex items-center space-x-3">
                <div className={getStatusColor(provider.status)}>
                  {getStatusIcon(provider.status)}
                </div>

                <div>
                  <div className="font-medium capitalize">{provider.name}</div>
                  <div className="text-sm text-muted-foreground">{provider.description}</div>
                  <div className="text-xs text-muted-foreground mt-1">
                    {provider.url} • {provider.type}
                  </div>
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <span
                  className={`text-xs px-2 py-1 rounded-full ${
                    provider.status === "available" || provider.status === "configured"
                      ? "bg-green-500/10 text-green-400"
                      : provider.status === "unavailable"
                        ? "bg-red-500/10 text-red-400"
                        : "bg-yellow-500/10 text-yellow-400"
                  }`}
                >
                  {provider.status.replace("_", " ")}
                </span>

                {provider.models && provider.models.length > 0 && (
                  <span className="text-xs text-muted-foreground">
                    {provider.models.length} models
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Model Management */}
      {currentProvider?.type === "local" && (
        <div className="card p-6">
          <h2 className="text-lg font-semibold mb-4">Model Management</h2>
          <p className="text-muted-foreground mb-6">
            Load and unload models for {currentProvider.name}. Local models need to be loaded into
            memory before use.
          </p>

          <div className="flex items-center space-x-4">
            <div className="flex-1">
              <label className="label">Model to Manage</label>
              <select
                value={selectedModel}
                onChange={(e) => {
                  setSelectedModel(e.target.value);
                  persistSelection(selectedProvider, e.target.value);
                }}
                className="input w-full"
                disabled={!currentProvider?.models?.length}
              >
                <option value="">Select a model...</option>
                {currentProvider?.models?.map((model) => (
                  <option key={model} value={model}>
                    {model}
                  </option>
                ))}
              </select>
            </div>

            <div className="flex space-x-2 pt-6">
              <button
                onClick={handleLoadModel}
                disabled={!selectedModel || isLoading}
                className="btn btn-primary flex items-center"
              >
                <Play className="h-4 w-4 mr-2" />
                Load
              </button>

              <button
                onClick={handleUnloadModel}
                disabled={!selectedModel || isLoading}
                className="btn btn-outline flex items-center"
              >
                <Square className="h-4 w-4 mr-2" />
                Unload
              </button>
            </div>
          </div>
        </div>
      )}

      {/* API Configuration */}
      {currentProvider?.type === "hosted" && (
        <div className="card p-6">
          <h2 className="text-lg font-semibold mb-4">API Configuration</h2>

          <div className="space-y-4">
            <div>
              <label className="label">API Key</label>
              <input
                type="password"
                placeholder={`Enter ${currentProvider.name.toUpperCase()} API key`}
                className="input w-full"
                onChange={onChange}
              />
              <p className="text-xs text-muted-foreground mt-1">
                Get your API key from{" "}
                <a
                  href={
                    currentProvider.name === "openai" ? "https://platform.openai.com/api-keys" : "#"
                  }
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-accent hover:underline"
                >
                  {currentProvider.name}.com
                </a>
              </p>
            </div>

            <div>
              <label className="label">Custom API Base URL (Optional)</label>
              <input
                type="url"
                placeholder="https://api.openai.com/v1"
                className="input w-full"
                onChange={onChange}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
