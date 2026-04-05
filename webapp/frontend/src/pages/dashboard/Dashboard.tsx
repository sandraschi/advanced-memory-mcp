import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Search, Book, Zap, Brain, TrendingUp, RefreshCw, Activity, Terminal, ShieldCheck, Globe } from 'lucide-react'
import ResearchCard from './ResearchCard'
import SkillCard from './SkillCard'
import { apiService } from '../../services/api'

interface ResearchItem {
  id: string
  title: string
  sources: string[]
  status: 'completed' | 'in_progress' | 'failed'
  timestamp: string
}

interface SkillItem {
  id: string
  title: string
  description: string
  sources: number
  created: string
}

export default function Dashboard() {
  const [recentResearch, setRecentResearch] = useState<ResearchItem[]>([])
  const [recentSkills, setRecentSkills] = useState<SkillItem[]>([])
  const [systemStatus, setSystemStatus] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isRefreshing, setIsRefreshing] = useState(false)

  const loadData = async () => {
    setIsRefreshing(true)
    try {
      const [researchResponse, skillsResponse, statusResponse] = await Promise.all([
        apiService.getRecentResearch(),
        apiService.getRecentSkills(),
        apiService.getSystemStatus()
      ])

      if (researchResponse?.success) {
        setRecentResearch(researchResponse.data || [])
      }

      if (skillsResponse?.success) {
        setRecentSkills(skillsResponse.data || [])
      }

      if (statusResponse?.success) {
        setSystemStatus(statusResponse.data)
      }
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
    } finally {
      setIsLoading(false)
      setIsRefreshing(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const handleRefresh = () => {
    loadData()
  }

  return (
    <div className="space-y-8 page-enter overflow-y-auto h-full pr-2 scrollbar-thin scrollbar-thumb-white/10">
      {/* Hero Section */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-indigo-900/40 via-black to-black border border-white/10 p-8 mb-8 indigo-glow">
        <div className="relative z-10 max-w-2xl">
          <h1 className="text-4xl font-bold tracking-tight text-white mb-4">Knowledge Management Layer</h1>
          <p className="text-lg text-indigo-200/70 mb-6">Structured research, zettelkasten organization, and automated skill generation.</p>
          <div className="flex gap-4">
            <button className="px-6 py-2.5 rounded-xl bg-indigo-600 text-white font-medium hover:bg-indigo-500 transition-all shadow-lg shadow-indigo-500/20 active:scale-95">New Research</button>
            <button className="px-6 py-2.5 rounded-xl bg-white/5 text-slate-300 font-medium border border-white/10 hover:bg-white/10 transition-all active:scale-95">Browse Skills</button>
          </div>
        </div>
        <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-500/20 blur-[120px] rounded-full -mr-20 -mt-20"></div>
      </div>

      {/* Quick Actions */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <div className="glass-card p-6 text-center cursor-pointer group">
          <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
            <Search className="h-6 w-6 text-indigo-400" />
          </div>
          <h3 className="font-bold text-white mb-1">New Research</h3>
          <p className="text-xs text-slate-500">Multi-source knowledge search</p>
        </div>

        <div className="glass-card p-6 text-center cursor-pointer group">
          <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
            <Zap className="h-6 w-6 text-indigo-400" />
          </div>
          <h3 className="font-bold text-white mb-1">Skill Library</h3>
          <p className="text-xs text-slate-500">Expert skill generation</p>
        </div>

        <div className="glass-card p-6 text-center cursor-pointer group">
          <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
            <Book className="h-6 w-6 text-indigo-400" />
          </div>
          <h3 className="font-bold text-white mb-1">Doc Ingest</h3>
          <p className="text-xs text-slate-500">PDF & Technical paper ingestion</p>
        </div>

        <Link to="/dashboard/canvas" className="block">
          <div className="glass-card p-6 text-center cursor-pointer group h-full">
            <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
              <Brain className="h-6 w-6 text-indigo-400" />
            </div>
            <h3 className="font-bold text-white mb-1">Knowledge Map</h3>
            <p className="text-xs text-slate-500">Graph-based semantic visualization</p>
          </div>
        </Link>
      </div>

      {/* Recent Activity */}
      <div className="grid gap-8 lg:grid-cols-7">
        {/* Recent Research */}
        <div className="col-span-4 glass-card p-6">
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center space-x-3">
              <div className="p-2 rounded-lg bg-indigo-500/10">
                <TrendingUp className="h-4 w-4 text-indigo-400" />
              </div>
              <h2 className="text-lg font-bold tracking-tight text-white">Neural Research Stream</h2>
              <button
                onClick={handleRefresh}
                disabled={isRefreshing}
                aria-label="Refresh Research Stream"
                className="p-1.5 rounded-lg hover:bg-white/5 text-slate-500 hover:text-white transition-all disabled:opacity-30"
              >
                <RefreshCw className={`h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
              </button>
            </div>
          </div>

          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-20 animate-pulse">
              <RefreshCw className="h-8 w-8 animate-spin text-indigo-500 mb-4" />
              <span className="text-sm font-medium text-slate-500">Synchronizing semantic weights...</span>
            </div>
          ) : (
            <div className="space-y-4">
              {recentResearch.length === 0 ? (
                <div className="text-center py-12 bg-white/[0.02] border border-dashed border-white/10 rounded-2xl">
                  <p className="text-sm text-slate-500">No active research cycles detected.</p>
                </div>
              ) : (
                recentResearch.map((research) => (
                  <ResearchCard key={research.id} research={research} />
                ))
              )}
            </div>
          )}
        </div>

        {/* Generated Skills */}
        <div className="col-span-3 glass-card p-6">
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center space-x-3">
              <div className="p-2 rounded-lg bg-indigo-500/10">
                <Brain className="h-4 w-4 text-indigo-400" />
              </div>
              <h2 className="text-lg font-bold tracking-tight text-white">Skill Library</h2>
            </div>
          </div>

          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-20 animate-pulse">
              <RefreshCw className="h-8 w-8 animate-spin text-indigo-500 mb-4" />
              <span className="text-sm font-medium text-slate-500">Loading skill manifests...</span>
            </div>
          ) : (
            <div className="space-y-4">
              {recentSkills.length === 0 ? (
                <div className="text-center py-12 bg-white/[0.02] border border-dashed border-white/10 rounded-2xl">
                  <p className="text-sm text-slate-500">Forge your first skill to begin.</p>
                </div>
              ) : (
                recentSkills.map((skill) => (
                  <SkillCard key={skill.id} skill={skill} />
                ))
              )}
            </div>
          )}
        </div>
      </div>

      {/* Engine Status */}
      <div className="glass-card p-6">
        <div className="flex items-center space-x-3 mb-8">
          <div className="p-2 rounded-lg bg-emerald-500/10">
            <Activity className="h-4 w-4 text-emerald-400" />
          </div>
          <h2 className="text-lg font-bold tracking-tight text-white">Core Connectivity Status</h2>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center py-6">
            <RefreshCw className="h-5 w-5 animate-spin text-slate-500" />
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-3">
            <div className="flex items-center justify-between p-5 bg-white/[0.03] border border-white/[0.06] rounded-2xl hover:bg-white/[0.05] transition-all">
              <div className="flex items-center">
                <Globe className="h-5 w-5 text-indigo-400 mr-4" />
                <div>
                  <p className="text-sm font-bold text-slate-100">LLM Engine</p>
                  <p className="text-xs text-slate-500 mt-1 font-mono uppercase tracking-wider">{systemStatus?.llm_model || 'GPT-4o'}</p>
                </div>
              </div>
              <div className="w-2.5 h-2.5 bg-emerald-500 rounded-full shadow-[0_0_10px_rgba(16,185,129,0.5)]"></div>
            </div>

            <div className="flex items-center justify-between p-5 bg-white/[0.03] border border-white/[0.06] rounded-2xl hover:bg-white/[0.05] transition-all">
              <div className="flex items-center">
                <Terminal className="h-5 w-5 text-indigo-400 mr-4" />
                <div>
                  <p className="text-sm font-bold text-slate-100">Knowledge Base</p>
                  <p className="text-xs text-slate-500 mt-1 uppercase tracking-wider">{systemStatus?.knowledge_base_size || 1247} Notes Integrated</p>
                </div>
              </div>
              <div className="w-2.5 h-2.5 bg-emerald-500 rounded-full shadow-[0_0_10px_rgba(16,185,129,0.5)]"></div>
            </div>

            <div className="flex items-center justify-between p-5 bg-white/[0.03] border border-white/[0.06] rounded-2xl hover:bg-white/[0.05] transition-all">
              <div className="flex items-center">
                <ShieldCheck className="h-5 w-5 text-indigo-400 mr-4" />
                <div>
                  <p className="text-sm font-bold text-slate-100">Security Access</p>
                  <p className="text-xs text-slate-500 mt-1 uppercase tracking-wider">L6 Federated Auth</p>
                </div>
              </div>
              <div className="w-2.5 h-2.5 bg-emerald-500 rounded-full shadow-[0_0_10px_rgba(16,185,129,0.5)]"></div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
