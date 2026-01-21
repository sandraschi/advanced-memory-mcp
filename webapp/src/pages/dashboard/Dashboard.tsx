import { Search, Book, Zap, Brain, TrendingUp } from 'lucide-react'
import HeroSection from './HeroSection'
import ResearchCard from './ResearchCard'
import SkillCard from './SkillCard'

export default function Dashboard() {
  const recentResearch = [
    {
      id: 1,
      title: "Brain Tumor Treatment Breakthroughs 2024",
      sources: ["Web (15 articles)", "arXiv (8 papers)", "Clinical Trials"],
      status: "completed",
      timestamp: "2026-01-20 14:31:40"
    },
    {
      id: 2,
      title: "Quantum Machine Learning Algorithms",
      sources: ["GitHub (12 repos)", "arXiv (6 papers)", "Web"],
      status: "in_progress",
      timestamp: "2026-01-20 14:45:22"
    }
  ]

  const recentSkills = [
    {
      id: 1,
      title: "Brain Tumor Treatment Expert",
      description: "Comprehensive knowledge of current glioblastoma treatments, clinical trials, and emerging therapies",
      sources: 31,
      created: "2026-01-20 14:31:40"
    },
    {
      id: 2,
      title: "Neural Network Architect",
      description: "Deep learning model design, optimization techniques, and implementation patterns",
      sources: 28,
      created: "2026-01-20 14:15:33"
    }
  ]

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

        <div className="card card-gold p-6 text-center hover:shadow-glow transition-shadow cursor-pointer group">
          <Brain className="h-8 w-8 text-accent mx-auto mb-3 group-hover:scale-110 transition-transform" />
          <h3 className="font-semibold mb-2">Knowledge Graph</h3>
          <p className="text-sm text-muted-foreground">Explore zettelkasten relationships</p>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="grid gap-8 lg:grid-cols-2">
        {/* Recent Research */}
        <div className="card p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold">Recent Research</h2>
            <TrendingUp className="h-5 w-5 text-accent" />
          </div>

          <div className="space-y-4">
            {recentResearch.map((research) => (
              <ResearchCard key={research.id} research={research} />
            ))}
          </div>
        </div>

        {/* Recent Skills */}
        <div className="card p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold">Generated Skills</h2>
            <Brain className="h-5 w-5 text-accent" />
          </div>

          <div className="space-y-4">
            {recentSkills.map((skill) => (
              <SkillCard key={skill.id} skill={skill} />
            ))}
          </div>
        </div>
      </div>

      {/* System Status */}
      <div className="card p-6">
        <h2 className="text-lg font-semibold mb-6">System Status</h2>

        <div className="grid gap-4 md:grid-cols-3">
          <div className="flex items-center justify-between p-4 bg-muted/50 rounded-md">
            <div>
              <div className="font-medium">LLM Provider</div>
              <div className="text-sm text-muted-foreground">Ollama (llama3:8b)</div>
            </div>
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
          </div>

          <div className="flex items-center justify-between p-4 bg-muted/50 rounded-md">
            <div>
              <div className="font-medium">Knowledge Base</div>
              <div className="text-sm text-muted-foreground">1,247 notes indexed</div>
            </div>
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
          </div>

          <div className="flex items-center justify-between p-4 bg-muted/50 rounded-md">
            <div>
              <div className="font-medium">Research APIs</div>
              <div className="text-sm text-muted-foreground">All services available</div>
            </div>
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
          </div>
        </div>
      </div>
    </div>
  )
}
