import { useState, useRef, useEffect } from 'react'
import { Mic, Square, Trash2, Wand2, FileAudio, FileText, Volume2, Sparkles, Loader2, Music } from 'lucide-react'

interface Recording {
    id: string
    title: string
    duration: string
    transcript: string
    distillation: string
    timestamp: string
}

export default function AudioHub() {
    const [isRecording, setIsRecording] = useState(false)
    const [recordings, setRecordings] = useState<Recording[]>([
        { id: '1', title: 'Philosophy Research Sync', duration: '02:45', transcript: 'The reductionist view of neural memory suggests a hardware-first approach to AGI...', distillation: 'Key Insight: Memory is purely physical reconfiguration. Action: Update Zettel #1.', timestamp: '2026-02-17' },
        { id: '2', title: 'MCP Technical Briefing', duration: '08:12', transcript: 'We are moving to FastMCP 2.14.4 for all internal servers to leverage the new transport layer...', distillation: 'Trend: Standardization on FastMCP. Impact: High.', timestamp: '2026-02-16' }
    ])
    const [selectedId, setSelectedId] = useState<string | null>(null)
    const [isDistilling, setIsDistilling] = useState(false)
    const [recordingTime, setRecordingTime] = useState(0)
    const timerRef = useRef<NodeJS.Timeout | null>(null)

    const selectedRecording = recordings.find(r => r.id === selectedId)

    useEffect(() => {
        if (isRecording) {
            timerRef.current = setInterval(() => {
                setRecordingTime(prev => prev + 1)
            }, 1000)
        } else {
            if (timerRef.current) clearInterval(timerRef.current)
            setRecordingTime(0)
        }
        return () => { if (timerRef.current) clearInterval(timerRef.current) }
    }, [isRecording])

    const formatTime = (seconds: number) => {
        const m = Math.floor(seconds / 60)
        const s = seconds % 60
        return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
    }

    const handleRecord = () => {
        setIsRecording(!isRecording)
        if (isRecording) {
            // Simulated stop and save
            const newRec: Recording = {
                id: Date.now().toString(),
                title: `Voice Note ${recordings.length + 1}`,
                duration: formatTime(recordingTime),
                transcript: '[SIMULATED TRANSCRIPTION] Data streams captured and synchronized with local GPU clusters...',
                distillation: '',
                timestamp: new Date().toISOString().slice(0, 10)
            }
            setRecordings([newRec, ...recordings])
            setSelectedId(newRec.id)
        }
    }

    const handleDistill = () => {
        if (!selectedId) return
        setIsDistilling(true)
        setTimeout(() => {
            setRecordings(prev => prev.map(r => r.id === selectedId ? {
                ...r,
                distillation: 'Distilled Intelligence: This recording covers multi-cluster synchronization and GPU optimization strategies. Link to Project #X.'
            } : r))
            setIsDistilling(false)
        }, 2000)
    }

    const handleDelete = (id: string) => {
        setRecordings(prev => prev.filter(r => r.id !== id))
        if (selectedId === id) setSelectedId(null)
    }

    return (
        <div className="max-w-[1400px] mx-auto h-[calc(100vh-12rem)] flex flex-col space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            {/* Header */}
            <div className="flex items-center justify-between shrink-0">
                <div className="flex items-center space-x-3">
                    <div className="p-2.5 bg-gradient-to-br from-indigo-500/20 to-blue-500/20 rounded-xl">
                        <Volume2 className="h-6 w-6 text-indigo-400" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold tracking-tight">Audio Hub</h1>
                        <p className="text-muted-foreground text-xs">Aural intelligence capture and distillation pipeline</p>
                    </div>
                </div>
            </div>

            {/* Main Content Areas */}
            <div className="flex-1 flex space-x-6 overflow-hidden min-h-0">
                {/* Left Pane: Capture & Archives */}
                <div className="w-80 shrink-0 flex flex-col space-y-4">
                    {/* Capture Card */}
                    <div className="card p-6 bg-gradient-to-br from-indigo-500/10 to-blue-500/10 border-indigo-500/20 relative overflow-hidden group">
                        <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                            <Mic className="h-24 w-24 text-indigo-400" />
                        </div>
                        <div className="relative z-10 space-y-6">
                            <div className="flex items-center justify-between">
                                <span className={`text-[10px] uppercase font-bold tracking-widest ${isRecording ? 'text-red-400 animate-pulse' : 'text-indigo-400'}`}>
                                    {isRecording ? 'Recording Active' : 'System Ready'}
                                </span>
                                <span className="text-xl font-mono font-bold">{formatTime(recordingTime)}</span>
                            </div>

                            <button
                                onClick={handleRecord}
                                className={`w-full py-4 rounded-xl flex items-center justify-center space-x-3 transition-all ${isRecording
                                    ? 'bg-red-500/20 border border-red-500/40 text-red-400'
                                    : 'bg-indigo-500/20 border border-indigo-500/40 text-indigo-400 hover:bg-indigo-500/30'
                                    }`}
                            >
                                {isRecording ? (
                                    <>
                                        <Square className="h-5 w-5 fill-current" />
                                        <span className="font-bold tracking-wider">STOP SESSION</span>
                                    </>
                                ) : (
                                    <>
                                        <Mic className="h-5 w-5" />
                                        <span className="font-bold tracking-wider">START CAPTURE</span>
                                    </>
                                )}
                            </button>
                        </div>
                    </div>

                    {/* Archives List */}
                    <div className="flex-1 flex flex-col min-h-0 space-y-2 overflow-y-auto pr-1 scrollbar-thin">
                        <label className="text-[10px] font-semibold uppercase tracking-widest text-muted-foreground px-2">Recent Archives</label>
                        {recordings.map(r => (
                            <button
                                key={r.id}
                                onClick={() => setSelectedId(r.id)}
                                className={`w-full text-left p-4 rounded-xl border transition-all ${selectedId === r.id
                                    ? 'bg-indigo-500/10 border-indigo-500/30'
                                    : 'bg-muted/10 border-white/5 hover:border-white/10 hover:bg-white/5'
                                    }`}
                            >
                                <div className="flex items-start justify-between mb-2">
                                    <h3 className={`font-semibold text-sm truncate ${selectedId === r.id ? 'text-indigo-400' : 'text-foreground'}`}>{r.title}</h3>
                                    <span className="text-[9px] text-muted-foreground font-mono">{r.duration}</span>
                                </div>
                                <p className="text-[10px] text-muted-foreground font-mono">{r.timestamp}</p>
                            </button>
                        ))}
                    </div>
                </div>

                {/* Center Pane: Transcript & Analysis */}
                <div className="flex-1 flex flex-col min-w-0">
                    {selectedId ? (
                        <div className="h-full flex flex-col space-y-4">
                            <div className="card flex-1 flex flex-col overflow-hidden p-0">
                                <div className="p-4 border-b border-white/5 flex items-center justify-between shrink-0">
                                    <div className="flex items-center space-x-3">
                                        <FileAudio className="h-4 w-4 text-indigo-400" />
                                        <h3 className="text-sm font-bold uppercase tracking-widest">{selectedRecording?.title}</h3>
                                    </div>
                                    <button onClick={() => handleDelete(selectedId)} className="p-2 hover:bg-red-500/10 text-red-400 rounded-lg transition-colors">
                                        <Trash2 className="h-4 w-4" />
                                    </button>
                                </div>

                                <div className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin">
                                    <div className="space-y-3">
                                        <label className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground flex items-center">
                                            <FileText className="h-3 w-3 mr-2" />
                                            STT Transcript
                                        </label>
                                        <p className="text-sm leading-relaxed text-muted-foreground bg-black/20 p-4 rounded-xl border border-white/5 italic">
                                            "{selectedRecording?.transcript}"
                                        </p>
                                    </div>

                                    {selectedRecording?.distillation ? (
                                        <div className="space-y-3 animate-in fade-in slide-in-from-bottom-4 duration-500">
                                            <label className="text-[10px] font-bold uppercase tracking-widest text-emerald-400 flex items-center">
                                                <Sparkles className="h-3 w-3 mr-2" />
                                                Distilled Insight
                                            </label>
                                            <div className="bg-emerald-500/5 border border-emerald-500/20 p-5 rounded-2xl relative group">
                                                <div className="absolute top-0 right-0 p-3 opacity-20">
                                                    <Wand2 className="h-12 w-12 text-emerald-400" />
                                                </div>
                                                <p className="text-sm text-emerald-100/80 leading-relaxed font-medium relative z-10">
                                                    {selectedRecording.distillation}
                                                </p>
                                            </div>
                                        </div>
                                    ) : (
                                        <button
                                            onClick={handleDistill}
                                            disabled={isDistilling}
                                            className="w-full py-8 border-2 border-dashed border-white/5 rounded-2xl hover:border-emerald-500/20 hover:bg-emerald-500/5 transition-all group flex flex-col items-center justify-center space-y-3"
                                        >
                                            {isDistilling ? (
                                                <Loader2 className="h-8 w-8 text-emerald-400 animate-spin" />
                                            ) : (
                                                <Wand2 className="h-8 w-8 text-muted-foreground group-hover:text-emerald-400 transition-colors" />
                                            )}
                                            <div className="text-center">
                                                <p className="text-sm font-bold uppercase tracking-widest text-muted-foreground group-hover:text-emerald-400 transition-colors">
                                                    {isDistilling ? 'Distilling Data...' : 'Run Distillation Pipeline'}
                                                </p>
                                                <p className="text-[10px] text-muted-foreground/50 mt-1">Cross-reference with knowledge base and tag semantic hooks.</p>
                                            </div>
                                        </button>
                                    )}
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="h-full card flex flex-col items-center justify-center text-center opacity-50 grayscale select-none">
                            <Music className="h-16 w-16 text-muted-foreground mb-4" />
                            <h3 className="text-xl font-bold">Sonic Archive</h3>
                            <p className="text-sm max-w-sm mt-2">Select a recording to analyze or start a new capture session to expand your aural intelligence.</p>
                        </div>
                    )}
                </div>

                {/* Right Pane: Timeline & Meta (Placeholder) */}
                <div className="w-80 shrink-0 space-y-4 flex flex-col">
                    <div className="card p-5 space-y-6">
                        <div className="flex items-center space-x-2 text-[10px] font-bold uppercase tracking-widest text-muted-foreground">
                            <Volume2 className="h-3.5 w-3.5" />
                            <span>Audio Metrics</span>
                        </div>
                        <div className="space-y-4">
                            <div className="space-y-1.5">
                                <div className="flex justify-between text-[10px]">
                                    <span className="text-muted-foreground">Capture Quality</span>
                                    <span className="text-emerald-400">Lossless</span>
                                </div>
                                <div className="w-full bg-white/5 h-1 rounded-full overflow-hidden">
                                    <div className="bg-emerald-400 h-full w-full" />
                                </div>
                            </div>
                            <div className="space-y-1.5">
                                <div className="flex justify-between text-[10px]">
                                    <span className="text-muted-foreground">Transciption Confidence</span>
                                    <span className="text-blue-400">98.2%</span>
                                </div>
                                <div className="w-full bg-white/5 h-1 rounded-full overflow-hidden">
                                    <div className="bg-blue-400 h-full w-[98%]" />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
