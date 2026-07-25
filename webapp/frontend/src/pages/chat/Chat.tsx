import {
  Bot,
  Download,
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

const HISTORY_KEY = "memops-chat-history";
const PERSONALITY_KEY = "memops-chat-personality";
const MAX_HISTORY = 100;

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

const personalities = [
  { id: "sandra", name: "Sandra", icon: Bot, description: "Materialist/Reductionist" },
  { id: "industrial", name: "Industrial", icon: Zap, description: "Direct/Efficient" },
  { id: "scientific", name: "Scientific", icon: Sliders, description: "Analytical/Rigorous" },
  { id: "creative", name: "Creative", icon: Sparkles, description: "Analogical/Aesthetic" },
];

const examplePrompts = [
  { group: "Memory", prompts: [
    "Search my knowledge graph for recent insights on AI safety",
    "What did I work on last week?",
    "Create a new note about transformer architectures",
  ]},
  { group: "Research", prompts: [
    "Summarize the latest arXiv papers on LLM alignment",
    "Find connected papers on multi-agent systems",
    "Compare these two research approaches",
  ]},
  { group: "Zettelkasten", prompts: [
    "Show me recent Zettelkasten notes",
    "Create a new Zettel linking AI and cognition",
    "Find orphan notes that need connections",
  ]},
];

function loadHistory(): Message[] {
  try { const raw = localStorage.getItem(HISTORY_KEY); return raw ? JSON.parse(raw) : []; } catch { return []; }
}

export default function Chat() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>(() => {
    const saved = loadHistory();
    return saved.length > 0 ? saved : [{
      role: "assistant",
      content: "Hello Sandra. I am your Advanced Memory Research Assistant. I am now configured for standard local LLM operations.",
      timestamp: new Date(),
    }];
  });
  const [isLoading, setIsLoading] = useState(false);
  const [personality, setPersonality] = useState(() => localStorage.getItem(PERSONALITY_KEY) || "sandra");
  const [refine, setRefine] = useState(false);
  const [models, setModels] = useState<any[]>([]);
  const [selectedModel, setSelectedModel] = useState("qwen2.5-coder:latest");
  const [skillName, setSkillName] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  // Persist messages
  useEffect(() => {
    try { localStorage.setItem(HISTORY_KEY, JSON.stringify(messages.slice(-MAX_HISTORY))); } catch {}
  }, [messages]);
  useEffect(() => { localStorage.setItem(PERSONALITY_KEY, personality); }, [personality]);

  // Load available models on mount
  useEffect(() => {
    const fetchModels = async () => {
      try {
        const response = await apiService.getLLMModels();
        if (response.success && Array.isArray(response.data)) {
          setModels(response.data);
          if (!response.data.some((m: any) => m.name === selectedModel) && response.data.length > 0) {
            setSelectedModel(response.data[0].name);
          }
        }
      } catch (error) {
        console.error("Failed to fetch models:", error);
      }
    };
    fetchModels();
  }, []);

  // Skill fetch
  useEffect(() => {
    (async () => {
      try {
        const r = await fetch("/api/skills");
        if (r.ok) {
          const data = await r.json();
          const skills = data?.skills ?? [];
          if (skills.length > 0) setSkillName(skills[0].name || skills[0]);
        }
      } catch {}
    })();
  }, []);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = { role: "user", content: input, timestamp: new Date() };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await apiService.chatQuery(input, { personality, model: selectedModel, refine });
      const assistantMessage: Message = {
        role: "assistant",
        content: response.success ? response.data : response.error || "I encountered an error processing your query.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      setMessages((prev) => [...prev, {
        role: "assistant",
        content: "Failed to communicate with the local LLM engine. Ensure Ollama is running.",
        timestamp: new Date(),
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const exportChat = () => {
    if (messages.length === 0) return;
    const lines = messages.map((m) => `[${m.timestamp.toISOString()}] ${m.role === "user" ? "You" : "AI"}: ${m.content}`);
    const blob = new Blob([lines.join("\n\n---\n\n")], { type: "text/plain" });
    const a = document.createElement("a"); a.href = URL.createObjectURL(blob);
    a.download = `memops-chat-${new Date().toISOString().slice(0, 10)}.txt`; a.click();
  };

  return (
    <div data-testid="chat-page" className="flex flex-col h-[calc(100vh-12rem)] max-w-5xl mx-auto">
      <div data-testid="chat-controls" className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <MessageSquare className="h-8 w-8 text-accent" />
          <h1 className="text-3xl font-bold tracking-tight">Standard Chat</h1>
          {skillName && <span className="text-[10px] text-zinc-500 bg-zinc-800 px-1.5 py-0.5 rounded font-mono">skill:{skillName}</span>}
        </div>

        <div className="flex items-center space-x-2">
          {/* Model Selector */}
          <select
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            className="bg-card border border-white/10 rounded-md px-3 py-1.5 text-xs focus:outline-none focus:ring-1 focus:ring-accent"
          >
            {models.length > 0 ? (
              models.map((m: any) => (
                <option key={m.name} value={m.name}>{m.name}</option>
              ))
            ) : (
              <option>No models found</option>
            )}
          </select>

          <button data-testid="chat-export" onClick={exportChat} disabled={messages.length === 0}
            className="p-2 text-muted-foreground hover:text-green-400 disabled:opacity-30 transition-colors" title="Export chat">
            <Download className="h-5 w-5" />
          </button>

          <button data-testid="chat-clear" onClick={() => { setMessages([{ role: "assistant", content: "Conversation cleared. How can I help you now?", timestamp: new Date() }]); localStorage.removeItem(HISTORY_KEY); }}
            className="p-2 text-muted-foreground hover:text-red-400 transition-colors" title="Clear conversation">
            <Trash2 className="h-5 w-5" />
          </button>
        </div>
      </div>

      {/* Config Bar */}
      <div className="flex flex-wrap items-center gap-4 mb-6 bg-card/30 p-3 rounded-xl border border-white/5">
        <div className="flex items-center space-x-2">
          <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Personality:</span>
          <div className="flex bg-background/50 rounded-lg p-1 border border-white/10" data-testid="personality-select">
            {personalities.map((p) => {
              const Icon = p.icon;
              return (
                <button
                  key={p.id}
                  onClick={() => setPersonality(p.id)}
                  className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-xs transition-all ${
                    personality === p.id ? "bg-accent text-accent-foreground shadow-sm" : "text-muted-foreground hover:text-foreground"
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
            <div className={`w-8 h-4 rounded-full p-0.5 transition-colors ${refine ? "bg-accent" : "bg-muted"}`}>
              <div className={`w-3 h-3 rounded-full bg-white transition-transform ${refine ? "translate-x-4" : "translate-x-0"}`} />
            </div>
            <input type="checkbox" className="hidden" checked={refine} onChange={(e) => setRefine(e.target.checked)} />
            <span className="text-xs font-medium group-hover:text-accent transition-colors">Refine Prompt</span>
          </label>
        </div>
      </div>

      <div data-testid="chat-messages" className="flex-1 overflow-y-auto pr-4 space-y-6 mb-6 scrollbar-thin">
        {messages.length === 0 && (
          <div className="text-center text-muted-foreground text-sm pt-8">
            <p>Ask about your knowledge graph, research, or notes.</p>
            <div data-testid="example-prompts" className="mt-6 max-w-lg mx-auto space-y-3">
              {examplePrompts.map((group) => (
                <div key={group.group}>
                  <p className="text-[10px] uppercase tracking-wider text-muted-foreground text-left mb-1.5 px-1">{group.group}</p>
                  <div className="flex flex-wrap gap-1.5 justify-center">
                    {group.prompts.map((p) => (
                      <button key={p} onClick={() => setInput(p)}
                        className="text-xs px-2.5 py-1.5 rounded-lg border border-white/10 bg-white/5 hover:bg-white/10 text-muted-foreground hover:text-foreground transition-colors text-left">
                        {p}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div className={`flex max-w-[80%] space-x-3 ${msg.role === "user" ? "flex-row-reverse space-x-reverse" : ""}`}>
              <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center border ${
                msg.role === "user" ? "bg-accent/10 border-accent/20 text-accent" : "bg-gold/10 border-gold/20 text-gold"
              }`}>
                {msg.role === "user" ? <User className="h-6 w-6" /> : <Bot className="h-6 w-6" />}
              </div>
              <div className={`p-4 rounded-2xl shadow-sm ${
                msg.role === "user" ? "bg-accent text-accent-foreground" : "bg-card border border-white/5 text-foreground"
              }`}>
                <div className="whitespace-pre-wrap leading-relaxed prose prose-invert prose-sm">{msg.content}</div>
                <div className={`text-[10px] mt-2 opacity-50 ${msg.role === "user" ? "text-right" : ""}`}>
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

      <form data-testid="chat-input-form" onSubmit={handleSend} className="relative">
        <input
          data-testid="chat-input"
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question..."
          className="w-full bg-card border border-white/10 rounded-full px-6 py-4 pr-16 focus:outline-none focus:ring-2 focus:ring-accent/50 shadow-lg text-lg"
          disabled={isLoading}
        />
        <button
          data-testid="chat-send"
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
