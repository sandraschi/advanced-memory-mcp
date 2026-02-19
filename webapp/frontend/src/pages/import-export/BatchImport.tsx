import { useState } from 'react'
import { FolderSearch, Filter, Calendar, FileText, CheckSquare, Square, Loader2, PlayCircle, ShieldCheck, AlertCircle } from 'lucide-react'
import { apiService } from '../../services/api'

interface ScannedFile {
    name: string
    path: string
    size: number
    modified: string
}

export default function BatchImport() {
    const [scanPath, setScanPath] = useState('D:\\Dev\\repos\\mcp-central-docs')
    const [months, setMonths] = useState(6)
    const [scannedFiles, setScannedFiles] = useState<ScannedFile[]>([])
    const [selectedPaths, setSelectedPaths] = useState<Set<string>>(new Set())
    const [isScanning, setIsScanning] = useState(false)
    const [isImporting, setIsImporting] = useState(false)
    const [results, setResults] = useState<any[] | null>(null)

    const handleScan = async () => {
        setIsScanning(true)
        setResults(null)
        try {
            const response = await apiService.scanImportDir(scanPath, months)
            if (response.success && response.data) {
                setScannedFiles(response.data)
                setSelectedPaths(new Set(response.data.map(f => f.path)))
            } else {
                alert(response.error || 'Scan failed')
            }
        } catch (err) {
            console.error(err)
        } finally {
            setIsScanning(false)
        }
    }

    const toggleSelect = (path: string) => {
        const next = new Set(selectedPaths)
        if (next.has(path)) next.delete(path)
        else next.add(path)
        setSelectedPaths(next)
    }

    const toggleSelectAll = () => {
        if (selectedPaths.size === scannedFiles.length) {
            setSelectedPaths(new Set())
        } else {
            setSelectedPaths(new Set(scannedFiles.map(f => f.path)))
        }
    }

    const handleImport = async () => {
        if (selectedPaths.size === 0) return
        setIsImporting(true)
        try {
            const response = await apiService.runBatchImport(Array.from(selectedPaths), 'batch_imports/docs')
            if (response.success) {
                setResults(response.data || [])
            } else {
                alert(response.error || 'Import failed')
            }
        } catch (err) {
            console.error(err)
        } finally {
            setIsImporting(false)
        }
    }

    return (
        <div className="max-w-5xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="flex items-center space-x-3">
                <div className="p-2 bg-accent/20 rounded-lg text-accent">
                    <FolderSearch className="h-8 w-8" />
                </div>
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Batch Repo Import</h1>
                    <p className="text-muted-foreground text-sm">Scan and ingest Markdown knowledge from external repositories</p>
                </div>
            </div>

            <div className="card p-6 bg-muted/20 border-white/5 space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="md:col-span-2 space-y-2">
                        <label className="text-sm font-medium flex items-center">
                            <FolderSearch className="h-4 w-4 mr-2" />
                            Repository Root Path
                        </label>
                        <input
                            value={scanPath}
                            onChange={e => setScanPath(e.target.value)}
                            className="w-full bg-background border border-border rounded-md px-4 py-2 outline-none focus:ring-2 focus:ring-accent/50"
                            placeholder="e.g. D:\Dev\repos\mcp-central-docs"
                        />
                    </div>
                    <div className="space-y-2">
                        <label className="text-sm font-medium flex items-center">
                            <Calendar className="h-4 w-4 mr-2" />
                            Recency Filter
                        </label>
                        <select
                            value={months}
                            onChange={e => setMonths(Number(e.target.value))}
                            className="w-full bg-background border border-border rounded-md px-4 py-2 outline-none cursor-pointer"
                        >
                            <option value={0}>All Files</option>
                            <option value={1}>Last 1 Month</option>
                            <option value={3}>Last 3 Months</option>
                            <option value={6}>Last 6 Months</option>
                            <option value={12}>Last Year</option>
                        </select>
                    </div>
                </div>

                <div className="flex justify-end">
                    <button
                        onClick={handleScan}
                        disabled={isScanning || !scanPath}
                        className="btn btn-primary px-8 flex items-center space-x-2 shadow-lg shadow-accent/20"
                    >
                        {isScanning ? <Loader2 className="h-4 w-4 animate-spin" /> : <Filter className="h-4 w-4" />}
                        <span>{isScanning ? 'Searching...' : 'Scan Repository'}</span>
                    </button>
                </div>
            </div>

            {scannedFiles.length > 0 && !results && (
                <div className="space-y-4 animate-in zoom-in-95 duration-300">
                    <div className="flex items-center justify-between px-2 text-sm text-muted-foreground">
                        <button
                            onClick={toggleSelectAll}
                            className="flex items-center space-x-2 hover:text-foreground transition-colors"
                        >
                            {selectedPaths.size === scannedFiles.length ? <CheckSquare className="h-4 w-4 text-accent" /> : <Square className="h-4 w-4" />}
                            <span>{selectedPaths.size} of {scannedFiles.length} files selected</span>
                        </button>
                    </div>

                    <div className="card overflow-hidden">
                        <div className="max-h-96 overflow-y-auto divide-y divide-white/5">
                            {scannedFiles.map(file => (
                                <div
                                    key={file.path}
                                    onClick={() => toggleSelect(file.path)}
                                    className={`p-4 flex items-center space-x-4 cursor-pointer hover:bg-white/5 transition-colors ${selectedPaths.has(file.path) ? 'bg-accent/5' : ''}`}
                                >
                                    {selectedPaths.has(file.path) ? <CheckSquare className="h-5 w-5 text-accent" /> : <Square className="h-5 w-5 text-muted-foreground/30" />}
                                    <FileText className="h-5 w-5 text-muted-foreground" />
                                    <div className="flex-1 min-w-0">
                                        <div className="font-medium truncate">{file.name}</div>
                                        <div className="text-[10px] uppercase font-mono text-muted-foreground/60">{file.path}</div>
                                    </div>
                                    <div className="text-right text-xs">
                                        <div className="text-muted-foreground">{(file.size / 1024).toFixed(1)} KB</div>
                                        <div className="text-[10px] text-muted-foreground/40">{new Date(file.modified).toLocaleDateString()}</div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="flex justify-center pt-4">
                        <button
                            onClick={handleImport}
                            disabled={isImporting || selectedPaths.size === 0}
                            className="btn btn-primary btn-lg flex items-center space-x-3 px-12 group"
                        >
                            {isImporting ? <Loader2 className="h-5 w-5 animate-spin" /> : <PlayCircle className="h-5 w-5 group-hover:scale-110 transition-transform" />}
                            <span className="text-lg">Ingest Selected Documents</span>
                        </button>
                    </div>
                </div>
            )}

            {results && (
                <div className="card p-8 text-center animate-in zoom-in-95 duration-500">
                    <ShieldCheck className="h-16 w-16 text-accent mx-auto mb-4" />
                    <h2 className="text-2xl font-bold mb-2">Import Workflow Complete</h2>
                    <p className="text-muted-foreground mb-8">
                        Successfully processed {results.filter(r => r.success).length} files.
                        {results.some(r => !r.success) && ` Failed: ${results.filter(r => !r.success).length}`}
                    </p>

                    <div className="max-h-64 overflow-y-auto text-left space-y-2 mb-8 bg-black/20 p-4 rounded-md border border-white/5">
                        {results.map((res, i) => (
                            <div key={i} className="flex items-center space-x-2 text-xs">
                                {res.success ? <CheckSquare className="h-3 w-3 text-accent" /> : <AlertCircle className="h-3 w-3 text-red-500" />}
                                <span className={res.success ? 'text-muted-foreground' : 'text-red-400'}>{res.path}</span>
                            </div>
                        ))}
                    </div>

                    <button onClick={() => setResults(null)} className="btn btn-outline">Start New Import</button>
                </div>
            )}
        </div>
    )
}
