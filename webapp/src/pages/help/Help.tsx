import { Book, Zap, Search, Settings, ExternalLink } from 'lucide-react'

export default function Help() {
  const sections = [
    {
      icon: Book,
      title: 'Getting Started',
      content: `
        Advanced Memory is a research-driven knowledge platform that transforms AI assistants into comprehensive research tools.

        Key features:
        • Multi-source research (web, academic papers, code repositories)
        • Intelligent skill creation from research findings
        • Document processing with RAG (Retrieval-Augmented Generation)
        • Zettelkasten-based knowledge management
      `
    },
    {
      icon: Search,
      title: 'Research Capabilities',
      content: `
        Access multiple research sources simultaneously:

        Web Intelligence:
        • DuckDuckGo, Google (SerpApi), Bing search
        • Time-based filtering (hours to years)
        • Domain-specific results

        Academic Research:
        • arXiv preprint database
        • Category-specific searches (AI, physics, math)
        • Citation analysis

        Code Intelligence:
        • GitHub repository analysis
        • Code search across millions of repositories
        • Implementation pattern discovery
      `
    },
    {
      icon: Zap,
      title: 'Skill Creation',
      content: `
        Create expert skills from multi-source research:

        Process:
        1. Define research topic
        2. Select sources (web, academic, code, documents)
        3. AI analyzes and synthesizes findings
        4. Generate structured skill with citations

        Examples:
        • Medical expert skills from clinical trials
        • Technical skills from academic papers
        • Creative writing from narrative analysis
      `
    },
    {
      icon: Settings,
      title: 'Configuration',
      content: `
        Customize your research environment:

        LLM Providers:
        • Ollama (local models)
        • LM Studio (local OpenAI-compatible)
        • OpenAI (hosted models)

        Research Settings:
        • Default search providers
        • Result limits and filters
        • Export preferences

        Knowledge Management:
        • Project organization
        • File indexing preferences
        • Export formats
      `
    }
  ]

  const quickActions = [
    {
      title: 'View Documentation',
      description: 'Complete user guide and API reference',
      action: () => window.open('#', '_blank')
    },
    {
      title: 'Open Settings',
      description: 'Configure LLM providers and research sources',
      action: () => window.location.href = '/settings'
    },
    {
      title: 'Try Research',
      description: 'Start your first multi-source research query',
      action: () => window.location.href = '/'
    }
  ]

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold mb-4">Advanced Memory Help</h1>
        <p className="text-xl text-muted-foreground">
          Transform any AI assistant into a research powerhouse with multi-source intelligence,
          academic literature access, code analysis, and intelligent skill creation.
        </p>
      </div>

      {/* Help sections */}
      <div className="grid gap-6 md:grid-cols-2">
        {sections.map((section, index) => (
          <div key={index} className="card card-gold p-6">
            <div className="flex items-start space-x-3">
              <div className="p-2 bg-accent/10 rounded-md">
                <section.icon className="h-5 w-5 text-accent" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold mb-3">{section.title}</h3>
                <div className="text-sm text-muted-foreground whitespace-pre-line">
                  {section.content}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Quick actions */}
      <div className="card p-6">
        <h2 className="text-lg font-semibold mb-6">Quick Actions</h2>
        <div className="grid gap-4 md:grid-cols-3">
          {quickActions.map((action, index) => (
            <button
              key={index}
              onClick={action.action}
              className="p-4 border border-border rounded-md hover:bg-muted/50 transition-colors text-left group"
            >
              <h4 className="font-medium mb-2 group-hover:text-accent transition-colors">
                {action.title}
              </h4>
              <p className="text-sm text-muted-foreground">
                {action.description}
              </p>
            </button>
          ))}
        </div>
      </div>

      {/* System info */}
      <div className="card p-6">
        <h2 className="text-lg font-semibold mb-4">System Information</h2>
        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <h4 className="font-medium mb-2">Version</h4>
            <p className="text-sm text-muted-foreground">Advanced Memory v1.2.0</p>
          </div>
          <div>
            <h4 className="font-medium mb-2">MCP Compatibility</h4>
            <p className="text-sm text-muted-foreground">FastMCP 2.14.3</p>
          </div>
          <div>
            <h4 className="font-medium mb-2">Supported Clients</h4>
            <p className="text-sm text-muted-foreground">Claude Desktop, Cursor, Windsurf</p>
          </div>
          <div>
            <h4 className="font-medium mb-2">Research Sources</h4>
            <p className="text-sm text-muted-foreground">15+ integrated providers</p>
          </div>
        </div>
      </div>

      {/* External links */}
      <div className="card p-6">
        <h2 className="text-lg font-semibold mb-4">Additional Resources</h2>
        <div className="space-y-3">
          <a
            href="#"
            className="flex items-center justify-between p-3 border border-border rounded-md hover:bg-muted/50 transition-colors group"
          >
            <div>
              <div className="font-medium group-hover:text-accent transition-colors">
                Full Documentation
              </div>
              <div className="text-sm text-muted-foreground">
                Complete user guide and API reference
              </div>
            </div>
            <ExternalLink className="h-4 w-4 text-muted-foreground group-hover:text-accent transition-colors" />
          </a>

          <a
            href="#"
            className="flex items-center justify-between p-3 border border-border rounded-md hover:bg-muted/50 transition-colors group"
          >
            <div>
              <div className="font-medium group-hover:text-accent transition-colors">
                GitHub Repository
              </div>
              <div className="text-sm text-muted-foreground">
                Source code, issues, and community
              </div>
            </div>
            <ExternalLink className="h-4 w-4 text-muted-foreground group-hover:text-accent transition-colors" />
          </a>
        </div>
      </div>
    </div>
  )
}
