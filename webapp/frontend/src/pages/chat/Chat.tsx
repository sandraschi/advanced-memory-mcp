import {
  Bot,
  Loader2,
  MessageSquare,
  Send,
  Sliders,
  Sparkles,
  Trash2,
  User,
  Zap,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { apiService } from "../../services/api";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

const personalities = [
  { id: "sandra", name: "Sandra (V12.1)", icon: Bot, description: "Materialist/Reductionist" },
  { id: "industrial", name: "Industrial", icon: Zap, description: "Direct/Efficient" },
  { id: "scientific", name: "Scientific", icon: Sliders, description: "Analytical/Rigorous" },
  { id: "creative", name: "Creative", icon: Sparkles, description: "Analogical/Aesthetic" },
];

export default function Chat() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hello Sandra. I am your Advanced Memory Research Assistant. I am now configured for standard local LLM operations.",
      timestamp: new Date(),
    },
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [personality, setPersonality] = useState("sandra");
  const [refine, setRefine] = useState(false);
  const [models, setModels] = useState<any[]>([]);
  const [selectedModel, setSelectedModel] = useState("qwen2.5-coder:latest");

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load available models on mount
  useEffect(() => {
    const fetchModels = async () => {
      try {
        const response = await apiService.getLLMModels();
        if (response.success && Array.isArray(response.data)) {
          setModels(response.data);
          // Auto-select first model if qwen is not found
          if (!response.data.some((m) => m.name === selectedModel) && response.data.length > 0) {
            setSelectedModel(response.data[0].name);
          }
        }
      } catch (error) {
        console.error("Failed to fetch models:", error);
      }
    };
    fetchModels();
  }, []);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      role: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await apiService.chatQuery(input, {
        personality,
        model: selectedModel,
        refine,
      });

      const assistantMessage: Message = {
        role: "assistant",
        content: response.success
          ? response.data
          : response.error || "I encountered an error processing your query.",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Failed to communicate with the local LLM engine. Ensure Ollama is running.",
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-12rem)] max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <MessageSquare className="h-8 w-8 text-accent" />
          <h1 className="text-3xl font-bold tracking-tight">Standard Chat</h1>
        </div>

        <div className="flex items-center space-x-2">
          {/* Model Selector */}
          <select
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            className="bg-card border border-white/10 rounded-md px-3 py-1.5 text-xs focus:outline-none focus:ring-1 focus:ring-accent"
          >
            {models.length > 0 ? (
              models.map((m) => (
                <option key={m.name} value={m.name}>
                  {m.name}
                </option>
              ))
            ) : (
              <option>No models found</option>
            )}
          </select>

          <button
            onClick={() =>
              setMessages([
                {
                  role: "assistant",
                  content: "Conversation cleared. How can I help you now?",
                  timestamp: new Date(),
                },
              ])
            }
            className="p-2 text-muted-foreground hover:text-red-400 transition-colors"
            title="Clear conversation"
          >
            <Trash2 className="h-5 w-5" />
          </button>
        </div>
      </div>

      {/* Config Bar */}
      <div className="flex flex-wrap items-center gap-4 mb-6 bg-card/30 p-3 rounded-xl border border-white/5">
        <div className="flex items-center space-x-2">
          <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
            Personality:
          </span>
          <div className="flex bg-background/50 rounded-lg p-1 border border-white/10">
            {personalities.map((p) => {
              const Icon = p.icon;
              return (
                <button
                  key={p.id}
                  onClick={() => setPersonality(p.id)}
                  className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-xs transition-all ${
                    personality === p.id
                      ? "bg-accent text-accent-foreground shadow-sm"
                      : "text-muted-foreground hover:text-foreground"
                  }`}
                  title={p.description}
                >
                  <Icon className="h-3.5 w-3.5" />
                  <span>{p.name.split(" ")[0]}</span>
                </button>
              );
            })}
          </div>
        </div>

        <div className="flex items-center space-x-2 border-l border-white/10 pl-4 ml-auto">
          <label className="flex items-center space-x-2 cursor-pointer group">
            <div
              className={`w-8 h-4 rounded-full p-0.5 transition-colors ${refine ? "bg-accent" : "bg-muted"}`}
            >
              <div
                className={`w-3 h-3 rounded-full bg-white transition-transform ${refine ? "translate-x-4" : "translate-x-0"}`}
              />
            </div>
            <input
              type="checkbox"
              className="hidden"
              checked={refine}
              onChange={(e) => setRefine(e.target.checked)}
            />
            <span className="text-xs font-medium group-hover:text-accent transition-colors">
              Refine Prompt
            </span>
          </label>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto pr-4 space-y-6 mb-6 scrollbar-thin">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`flex max-w-[80%] space-x-3 ${msg.role === "user" ? "flex-row-reverse space-x-reverse" : ""}`}
            >
              <div
                className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center border ${
                  msg.role === "user"
                    ? "bg-accent/10 border-accent/20 text-accent"
                    : "bg-gold/10 border-gold/20 text-gold"
                }`}
              >
                {msg.role === "user" ? <User className="h-6 w-6" /> : <Bot className="h-6 w-6" />}
              </div>
              <div
                className={`p-4 rounded-2xl shadow-sm ${
                  msg.role === "user"
                    ? "bg-accent text-accent-foreground"
                    : "bg-card border border-white/5 text-foreground"
                }`}
              >
                <div className="whitespace-pre-wrap leading-relaxed prose prose-invert prose-sm">
                  {msg.content}
                </div>
                <div
                  className={`text-[10px] mt-2 opacity-50 ${msg.role === "user" ? "text-right" : ""}`}
                >
                  {msg.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                </div>
              </div>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start animate-in fade-in slide-in-from-left-2 transition-all">
            <div className="flex max-w-[80%] space-x-3">
              <div className="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center border bg-gold/10 border-gold/20 text-gold">
                <Bot className="h-6 w-6" />
              </div>
              <div className="p-4 rounded-2xl bg-card border border-white/5 flex items-center space-x-2">
                <Loader2 className="h-4 w-4 animate-spin text-accent" />
                <span className="text-sm text-muted-foreground">Thinking (Local LLM)...</span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSend} className="relative">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question..."
          className="w-full bg-card border border-white/10 rounded-full px-6 py-4 pr-16 focus:outline-none focus:ring-2 focus:ring-accent/50 shadow-lg text-lg"
          disabled={isLoading}
        />
        <button
          type="submit"
          disabled={!input.trim() || isLoading}
          className="absolute right-3 top-1/2 -translate-y-1/2 p-2 bg-accent text-accent-foreground rounded-full hover:bg-accent/80 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md"
        >
          <Send className="h-6 w-6" />
        </button>
      </form>

      <div className="mt-4 text-center">
        <p className="text-xs text-muted-foreground flex items-center justify-center">
          <Loader2 className="h-3 w-3 mr-1" />
          Direct Local LLM Connection (Ollama)
        </p>
      </div>
    </div>
  );
}
