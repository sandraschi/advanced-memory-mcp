import { X, Book, Zap, Search, Settings } from 'lucide-react'

interface HelpModalProps {
  isOpen: boolean
  onClose: () => void
}

const helpSections = [
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

export default function HelpModal({ isOpen, onClose }: HelpModalProps) {
  if (!isOpen) return null

  return (
    <div className="modal-overlay">
      <div className="modal-content max-w-4xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-border pb-4">
          <h2 className="text-lg font-semibold">Advanced Memory Help</h2>
          <button
            onClick={onClose}
            className="p-2 rounded-md hover:bg-muted transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content */}
        <div className="py-6 overflow-auto max-h-[70vh]">
          <div className="space-y-6">
            {/* Introduction */}
            <div className="text-center pb-6 border-b border-border">
              <h3 className="text-xl font-semibold mb-2">Welcome to Advanced Memory</h3>
              <p className="text-muted-foreground">
                Transform any AI assistant into a research powerhouse with multi-source intelligence,
                academic literature access, and intelligent skill creation.
              </p>
            </div>

            {/* Help sections */}
            <div className="grid gap-6 md:grid-cols-2">
              {helpSections.map((section, index) => (
                <div key={index} className="card card-gold p-6">
                  <div className="flex items-start space-x-3">
                    <div className="p-2 bg-accent/10 rounded-md">
                      <section.icon className="h-5 w-5 text-accent" />
                    </div>
                    <div className="flex-1">
                      <h4 className="font-semibold mb-3">{section.title}</h4>
                      <div className="text-sm text-muted-foreground whitespace-pre-line">
                        {section.content}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Quick actions */}
            <div className="pt-6 border-t border-border">
              <h4 className="font-semibold mb-4">Quick Actions</h4>
              <div className="grid gap-3 md:grid-cols-3">
                <button className="btn btn-outline justify-start">
                  <Book className="h-4 w-4 mr-2" />
                  View Documentation
                </button>
                <button className="btn btn-outline justify-start">
                  <Settings className="h-4 w-4 mr-2" />
                  Open Settings
                </button>
                <button className="btn btn-outline justify-start">
                  <Zap className="h-4 w-4 mr-2" />
                  Try Research
                </button>
              </div>
            </div>

            {/* Support */}
            <div className="pt-6 border-t border-border text-center">
              <p className="text-sm text-muted-foreground mb-2">
                Need more help?
              </p>
              <p className="text-sm">
                Check the <a href="#" className="text-accent hover:underline">full documentation</a> or
                visit our <a href="#" className="text-accent hover:underline">GitHub repository</a>.
              </p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex justify-end pt-4 border-t border-border">
          <button onClick={onClose} className="btn btn-primary">
            Close
          </button>
        </div>
      </div>
    </div>
  )
}
