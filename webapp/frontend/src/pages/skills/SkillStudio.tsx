import { useState } from 'react'
import { Sparkles, Terminal, FileCode, Check, ChevronRight, Brain, Shield, Rocket, Info, RefreshCw, Layers, Database, ExternalLink } from 'lucide-react'

export default function SkillStudio() {
    const [step, setStep] = useState(1)
    const [skillName, setSkillName] = useState('')
    const [description, setDescription] = useState('')
    const [isGenerating, setIsGenerating] = useState(false)
    const [progress, setProgress] = useState(0)

    const steps = [
        { id: 1, name: 'Conceptualize', icon: Brain },
        { id: 2, name: 'Synthesize', icon: Sparkles },
        { id: 3, name: 'Validate', icon: Shield },
        { id: 4, name: 'Deploy', icon: Rocket },
    ]

    const handleGenerate = () => {
        setIsGenerating(true)
        setProgress(0)
        const interval = setInterval(() => {
            setProgress(prev => {
                if (prev >= 100) {
                    clearInterval(interval)
                    setIsGenerating(false)
                    setStep(3)
                    return 100
                }
                return prev + 2
            })
        }, 50)
    }

    return (
        <div className="flex flex-col h-full bg-background overflow-hidden">
            {/* Studio Header */}
            <div className="px-12 py-10 border-b border-white/5 bg-black/20">
                <div className="flex items-center justify-between max-w-5xl mx-auto">
                    <div className="flex items-center space-x-4">
                        <div className="p-3 bg-amber-500/20 rounded-2xl">
                            <Layers className="h-6 w-6 text-amber-500" />
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold tracking-tight">Skill Synthesis Studio</h1>
                            <p className="text-xs text-muted-foreground uppercase tracking-widest font-bold">Forge Agent Intelligence v1.3.0</p>
                        </div>
                    </div>

                    <div className="flex items-center space-x-8">
                        {steps.map((s, i) => (
                            <div key={s.id} className="flex items-center">
                                <div className={`flex flex-col items-center space-y-2 transition-opacity ${step >= s.id ? 'opacity-100' : 'opacity-30'}`}>
                                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold border-2 ${step > s.id ? 'bg-amber-500 text-black border-amber-500' : step === s.id ? 'border-amber-500 text-amber-500' : 'border-white/20 text-white/20'}`}>
                                        {step > s.id ? <Check className="h-4 w-4" /> : s.id}
                                    </div>
                                    <span className="text-[10px] uppercase font-bold tracking-widest">{s.name}</span>
                                </div>
                                {i < steps.length - 1 && (
                                    <div className={`w-12 h-px mx-4 transition-colors ${step > s.id ? 'bg-amber-500' : 'bg-white/10'}`} />
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="flex-1 p-12 overflow-y-auto scrollbar-thin">
                <div className="max-w-5xl mx-auto grid grid-cols-12 gap-12">

                    {/* Left Column: Editor/Wizard */}
                    <div className="col-span-12 lg:col-span-7 space-y-10">
                        {step === 1 && (
                            <div className="space-y-8 animate-in fade-in slide-in-from-left-4 duration-500">
                                <div className="space-y-4">
                                    <h2 className="text-xl font-bold">Conceptualize Intelligence</h2>
                                    <p className="text-sm text-muted-foreground">Define the purpose and scope of the new skill. Our synthesis engine will use your Zettelkasten as primary reference.</p>
                                </div>

                                <div className="space-y-6">
                                    <div className="space-y-3">
                                        <label className="text-[10px] uppercase font-bold tracking-widest text-muted-foreground ml-1">Skill Name (Unique ID)</label>
                                        <input
                                            type="text"
                                            value={skillName}
                                            onChange={(e) => setSkillName(e.target.value)}
                                            placeholder="e.g. quantum-computing-expert"
                                            className="w-full bg-white/5 border border-white/10 rounded-2xl p-4 text-sm focus:outline-none focus:ring-1 focus:ring-amber-500/50 transition-all font-mono"
                                        />
                                    </div>
                                    <div className="space-y-3">
                                        <label className="text-[10px] uppercase font-bold tracking-widest text-muted-foreground ml-1">Contextual Description</label>
                                        <textarea
                                            value={description}
                                            onChange={(e) => setDescription(e.target.value)}
                                            placeholder="Describe the specialized capabilities..."
                                            rows={4}
                                            className="w-full bg-white/5 border border-white/10 rounded-2xl p-4 text-sm focus:outline-none focus:ring-1 focus:ring-amber-500/50 transition-all resize-none"
                                        />
                                    </div>
                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="bg-white/2 border border-white/5 p-4 rounded-2xl hover:bg-white/5 transition-colors cursor-pointer group">
                                            <div className="flex items-center space-x-3 mb-2">
                                                <Database className="h-4 w-4 text-amber-500" />
                                                <span className="text-xs font-bold">Knowledge Driven</span>
                                            </div>
                                            <p className="text-[10px] text-muted-foreground leading-relaxed">Synthesize from existing Zettelkasten and research nodes.</p>
                                        </div>
                                        <div className="bg-white/2 border border-white/5 p-4 rounded-2xl border-amber-500/20 bg-amber-500/5 group">
                                            <div className="flex items-center space-x-3 mb-2">
                                                <Terminal className="h-4 w-4 text-amber-500" />
                                                <span className="text-xs font-bold">Tool Focused</span>
                                            </div>
                                            <p className="text-[10px] text-muted-foreground leading-relaxed">Design specialized terminal and filesystem automation routines.</p>
                                        </div>
                                    </div>
                                </div>

                                <button
                                    onClick={() => setStep(2)}
                                    disabled={!skillName || !description}
                                    className="flex items-center space-x-2 bg-white text-black px-8 py-3 rounded-xl font-bold text-sm hover:bg-amber-500 transition-all disabled:opacity-20"
                                >
                                    <span>Continue to Synthesis</span>
                                    <ChevronRight className="h-4 w-4" />
                                </button>
                            </div>
                        )}

                        {step === 2 && (
                            <div className="space-y-10 animate-in fade-in slide-in-from-left-4 duration-500">
                                <div className="space-y-4 text-center py-20 bg-black/20 border border-white/5 rounded-3xl relative overflow-hidden">
                                    {isGenerating ? (
                                        <>
                                            <div className="relative z-10 flex flex-col items-center">
                                                <div className="relative mb-8">
                                                    <Sparkles className="h-16 w-16 text-amber-500 animate-pulse" />
                                                    <div className="absolute inset-0 bg-amber-500/20 blur-3xl rounded-full" />
                                                </div>
                                                <h3 className="text-2xl font-bold mb-2">Synthesizing Intelligence</h3>
                                                <p className="text-sm text-muted-foreground mb-8 italic">Traversing knowledge graph to build authoritative SKILL.md...</p>

                                                <div className="w-64 h-2 bg-white/10 rounded-full overflow-hidden">
                                                    <div
                                                        className="h-full bg-amber-500 transition-all duration-300 ease-out"
                                                        style={{ width: `${progress}%` }}
                                                    />
                                                </div>
                                                <span className="mt-2 text-[10px] font-mono text-amber-500">{progress}%</span>
                                            </div>

                                            {/* DNA Background Animation Mock */}
                                            <div className="absolute inset-0 opacity-10 pointer-events-none">
                                                <div className="absolute top-0 left-1/2 w-px h-full bg-gradient-to-b from-transparent via-amber-500 to-transparent" />
                                                <div className="absolute top-1/4 left-0 w-full h-px bg-gradient-to-r from-transparent via-amber-500 to-transparent animate-pulse" />
                                            </div>
                                        </>
                                    ) : (
                                        <div className="flex flex-col items-center">
                                            <Check className="h-12 w-12 text-green-500 mb-4" />
                                            <h3 className="text-xl font-bold">Synthesis Complete</h3>
                                            <p className="text-sm text-muted-foreground mb-8">Generated 356 lines of structured expert instructions.</p>
                                            <button
                                                onClick={handleGenerate}
                                                className="bg-amber-500 text-black px-8 py-3 rounded-xl font-bold text-sm hover:bg-amber-400 transition-all flex items-center space-x-2"
                                            >
                                                <RefreshCw className="h-4 w-4" />
                                                <span>Re-Synthesize</span>
                                            </button>
                                        </div>
                                    )}
                                </div>

                                {!isGenerating && (
                                    <div className="bg-green-500/10 border border-green-500/20 p-6 rounded-2xl flex items-start space-x-4">
                                        <Shield className="h-5 w-5 text-green-500 mt-1" />
                                        <div className="space-y-1">
                                            <p className="text-xs font-bold text-green-500">Validation Passed</p>
                                            <p className="text-[10px] text-muted-foreground">All instructions comply with the Thermodynamic Behavioral Standards defined in GEMINI.md.</p>
                                        </div>
                                    </div>
                                )}

                                {!isGenerating && (
                                    <button
                                        onClick={() => setStep(3)}
                                        className="flex items-center space-x-2 bg-white text-black px-8 py-3 rounded-xl font-bold text-sm hover:bg-amber-500 transition-all"
                                    >
                                        <span>Proceed to Validation</span>
                                        <ChevronRight className="h-4 w-4" />
                                    </button>
                                )}
                            </div>
                        )}

                        {step === 3 && (
                            <div className="space-y-8 animate-in fade-in slide-in-from-left-4 duration-500">
                                <div className="space-y-4">
                                    <h2 className="text-xl font-bold">Final Validation & Manual Audit</h2>
                                    <p className="text-sm text-muted-foreground">Review the synthesized instruction block before committing to the local depot.</p>
                                </div>

                                <div className="bg-black/60 border border-white/10 rounded-2xl overflow-hidden shadow-2xl">
                                    <div className="bg-white/5 border-b border-white/5 px-6 py-3 flex items-center justify-between">
                                        <div className="flex items-center space-x-3">
                                            <FileCode className="h-4 w-4 text-amber-500" />
                                            <span className="text-[10px] font-mono text-muted-foreground uppercase tracking-widest leading-none mt-0.5">SKILL.md (Synthesized)</span>
                                        </div>
                                        <div className="flex space-x-1.5 leading-none">
                                            <div className="w-2.5 h-2.5 rounded-full bg-white/10" />
                                            <div className="w-2.5 h-2.5 rounded-full bg-white/10" />
                                            <div className="w-2.5 h-2.5 rounded-full bg-white/10" />
                                        </div>
                                    </div>
                                    <div className="p-8 font-mono text-xs text-muted-foreground space-y-4 max-h-96 overflow-y-auto scrollbar-thin">
                                        <p className="text-white"># {skillName}</p>
                                        <p className="text-amber-500/80 italic">{"<instruction_block>"}</p>
                                        <p>You are an expert in {skillName}. Your goal is to assist the user by providing deep insights extracted from the Advanced Memory knowledge graph.</p>
                                        <p>## Core Logic</p>
                                        <ul className="list-disc ml-4 space-y-2">
                                            <li>Always prioritize data-driven conclusions.</li>
                                            <li>Use the `adn_research` tool for real-time validation.</li>
                                            <li>Maintain a materialist/reductionist tone at all times.</li>
                                        </ul>
                                        <p>## Security Protocols</p>
                                        <p>Always audit skill calls against the ClawHub malware index (AMOS detection active).</p>
                                        <p className="text-amber-500/80 italic">{"</instruction_block>"}</p>
                                    </div>
                                </div>

                                <div className="flex items-center space-x-4">
                                    <button
                                        onClick={() => setStep(4)}
                                        className="bg-amber-500 text-black px-10 py-3 rounded-xl font-bold text-sm hover:bg-amber-400 transition-all flex items-center space-x-2 shadow-lg shadow-amber-500/20"
                                    >
                                        <Rocket className="h-4 w-4" />
                                        <span>Commit to Depot</span>
                                    </button>
                                    <button
                                        onClick={() => setStep(1)}
                                        className="bg-white/5 text-white border border-white/10 px-8 py-3 rounded-xl font-bold text-sm hover:bg-white/10 transition-all"
                                    >
                                        Edit Blueprint
                                    </button>
                                </div>
                            </div>
                        )}

                        {step === 4 && (
                            <div className="space-y-10 animate-in fade-in slide-in-from-bottom-4 duration-700 py-10">
                                <div className="flex flex-col items-center text-center space-y-6">
                                    <div className="relative">
                                        <Shield className="h-20 w-20 text-blue-500" />
                                        <Check className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 h-8 w-8 text-black bg-white rounded-full p-1" />
                                    </div>
                                    <div className="space-y-2">
                                        <h2 className="text-3xl font-bold">Skill Successfully Deployed</h2>
                                        <p className="text-muted-foreground max-w-sm mx-auto">The `{skillName}` intelligence node is now active in your global depot and recognized by all IDE rules.</p>
                                    </div>
                                    <div className="bg-white/5 border border-white/10 p-4 rounded-xl font-mono text-[10px] text-amber-500">
                                        PATH: ~/.gemini/antigravity/skills/{skillName}/
                                    </div>
                                    <div className="flex space-x-4 pt-4">
                                        <button
                                            onClick={() => { setStep(1); setSkillName(''); setDescription(''); }}
                                            className="bg-white text-black px-8 py-3 rounded-xl font-bold text-sm hover:bg-amber-500 transition-all"
                                        >
                                            Forge New Intelligence
                                        </button>
                                        <button className="bg-white/5 text-white border border-white/10 px-8 py-3 rounded-xl font-bold text-sm hover:bg-white/10 transition-all flex items-center space-x-2">
                                            <span>View in Marketplace</span>
                                            <ExternalLink className="h-4 w-4" />
                                        </button>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Right Column: Meta Info */}
                    <div className="col-span-12 lg:col-span-5">
                        <div className="sticky top-0 space-y-8">
                            <div className="bg-black/40 backdrop-blur-xl border border-white/10 rounded-3xl p-8 space-y-6">
                                <div className="flex items-center space-x-2 opacity-60">
                                    <Info className="h-4 w-4" />
                                    <span className="text-[10px] uppercase font-bold tracking-widest">Synthesis Engine Status</span>
                                </div>

                                <div className="space-y-6">
                                    <div className="space-y-3">
                                        <div className="flex items-center justify-between text-xs font-bold">
                                            <span>Knowledge Integration</span>
                                            <span className="text-amber-500">84%</span>
                                        </div>
                                        <div className="h-1 bg-white/5 rounded-full overflow-hidden">
                                            <div className="h-full w-[84%] bg-amber-500" />
                                        </div>
                                    </div>
                                    <div className="space-y-3">
                                        <div className="flex items-center justify-between text-xs font-bold">
                                            <span>Semantic Coherence</span>
                                            <span className="text-blue-500">96%</span>
                                        </div>
                                        <div className="h-1 bg-white/5 rounded-full overflow-hidden">
                                            <div className="h-full w-[96%] bg-blue-500" />
                                        </div>
                                    </div>
                                    <div className="space-y-3">
                                        <div className="flex items-center justify-between text-xs font-bold">
                                            <span>Malware Vector Check</span>
                                            <span className="text-green-500">CLEAN</span>
                                        </div>
                                        <div className="h-1 bg-white/5 rounded-full overflow-hidden">
                                            <div className="h-full w-full bg-green-500/50" />
                                        </div>
                                    </div>
                                </div>

                                <div className="pt-4 space-y-4 border-t border-white/5">
                                    <div className="flex items-center justify-between text-[10px] uppercase font-bold tracking-tight opacity-40">
                                        <span>Synthesis Engine</span>
                                        <span>Gemini 3 Pro</span>
                                    </div>
                                    <div className="flex items-center justify-between text-[10px] uppercase font-bold tracking-tight opacity-40">
                                        <span>Build Pipeline</span>
                                        <span>FastMCP 2.14.4+</span>
                                    </div>
                                    <div className="flex items-center justify-between text-[10px] uppercase font-bold tracking-tight opacity-40">
                                        <span>Observability</span>
                                        <span>Entire.io Active</span>
                                    </div>
                                </div>
                            </div>

                            <div className="bg-amber-500/5 border border-amber-500/20 rounded-3xl p-8">
                                <h4 className="text-xs font-bold text-amber-500 uppercase tracking-widest mb-4">Pro Tip: Depot Mapping</h4>
                                <p className="text-[10px] text-muted-foreground leading-relaxed">
                                    Synthesized skills are automatically mapped to your IDE rules. If you see "Malware Detected," the engine will isolate the skill in a sandbox and require manual binary auditing.
                                </p>
                            </div>
                        </div>
                    </div>

                </div>
            </div>
        </div>
    )
}
