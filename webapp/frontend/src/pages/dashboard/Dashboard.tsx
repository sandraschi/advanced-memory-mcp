import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Search, Book, Zap, Brain, TrendingUp, RefreshCw } from 'lucide-react'
import HeroSection from './HeroSection'
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

      if (researchResponse.success) {
        setRecentResearch(researchResponse.data || [])
      }

      if (skillsResponse.success) {
        setRecentSkills(skillsResponse.data || [])
      }

      if (statusResponse.success) {
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
    <div className="space-y-8">
      {/* Hero Section */}
      <HeroSection />

      {/* Quick Actions */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <div className="card card-gold p-6 text-center hover:shadow-glow transition-shadow cursor-pointer group">
          <Search className="h-8 w-8 text-accent mx-auto mb-3 group-hover:scale-110 transition-transform" />
          <h3 className="font-semibold mb-2">New Research</h3>
          <p className="text-sm text-muted-foreground">Start multi-source research</p>
        </div>

        <div className="card card-gold p-6 text-center hover:shadow-glow transition-shadow cursor-pointer group">
          <Zap className="h-8 w-8 text-accent mx-auto mb-3 group-hover:scale-110 transition-transform" />
          <h3 className="font-semibold mb-2">Create Skill</h3>
          <p className="text-sm text-muted-foreground">Generate expert from research</p>
        </div>

        <div className="card card-gold p-6 text-center hover:shadow-glow transition-shadow cursor-pointer group">
          <Book className="h-8 w-8 text-accent mx-auto mb-3 group-hover:scale-110 transition-transform" />
          <h3 className="font-semibold mb-2">Document Analysis</h3>
          <p className="text-sm text-muted-foreground">Process PDFs and research papers</p>
        </div>

        <Link to="/knowledge-graph" className="block">
          <div className="card card-gold p-6 text-center hover:shadow-glow transition-shadow cursor-pointer group">
            <Brain className="h-8 w-8 text-accent mx-auto mb-3 group-hover:scale-110 transition-transform" />
            <h3 className="font-semibold mb-2">Knowledge Graph</h3>
            <p className="text-sm text-muted-foreground">Explore zettelkasten relationships</p>
          </div>
        </Link>
      </div>

      {/* Recent Activity */}
      <div className="grid gap-8 lg:grid-cols-2">
        {/* Recent Research */}
        <div className="card p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-2">
              <h2 className="text-lg font-semibold">Recent Research</h2>
              <button
                onClick={handleRefresh}
                disabled={isRefreshing}
                className="p-1 rounded-md hover:bg-muted transition-colors"
                title="Refresh data"
              >
                <RefreshCw className={`h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
              </button>
            </div>
            <TrendingUp className="h-5 w-5 text-accent" />
          </div>

          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <RefreshCw className="h-6 w-6 animate-spin text-muted-foreground" />
              <span className="ml-2 text-muted-foreground">Loading research data...</span>
            </div>
          ) : (
            <div className="space-y-4">
              {recentResearch.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  No recent research found. Start your first research query above.
                </div>
              ) : (
                recentResearch.map((research) => (
                  <ResearchCard key={research.id} research={research} />
                ))
              )}
            </div>
          )}
        </div>

        {/* Recent Skills */}
        <div className="card p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold">Generated Skills</h2>
            <Brain className="h-5 w-5 text-accent" />
          </div>

          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <RefreshCw className="h-6 w-6 animate-spin text-muted-foreground" />
              <span className="ml-2 text-muted-foreground">Loading skills data...</span>
            </div>
          ) : (
            <div className="space-y-4">
              {recentSkills.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  No skills generated yet. Create your first expert skill above.
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

      {/* System Status */}
      <div className="card p-6">
        <h2 className="text-lg font-semibold mb-6">System Status</h2>

        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <RefreshCw className="h-6 w-6 animate-spin text-muted-foreground" />
            <span className="ml-2 text-muted-foreground">Checking system status...</span>
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-3">
            <div className="flex items-center justify-between p-4 bg-muted/50 rounded-md">
              <div>
                <div className="font-medium">LLM Provider</div>
                <div className="text-sm text-muted-foreground">
                  {systemStatus?.llm_provider || 'ollama'} ({systemStatus?.llm_model || 'llama3:8b'})
                </div>
              </div>
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            </div>

            <div className="flex items-center justify-between p-4 bg-muted/50 rounded-md">
              <div>
                <div className="font-medium">Knowledge Base</div>
                <div className="text-sm text-muted-foreground">
                  {systemStatus?.knowledge_base_size || 1247} notes indexed
                </div>
              </div>
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            </div>

            <div className="flex items-center justify-between p-4 bg-muted/50 rounded-md">
              <div>
                <div className="font-medium">Research APIs</div>
                <div className="text-sm text-muted-foreground">
                  {systemStatus?.research_apis_status || 'All services available'}
                </div>
              </div>
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
