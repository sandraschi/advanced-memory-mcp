import { Clock, CheckCircle, Loader } from 'lucide-react'

interface Research {
  id: string
  title: string
  sources: string[]
  status: 'completed' | 'in_progress' | 'failed'
  timestamp: string
}

interface ResearchCardProps {
  research: Research
}

const statusConfig = {
  completed: {
    icon: CheckCircle,
    color: 'text-green-400',
    bgColor: 'bg-green-500/10',
    text: 'Completed'
  },
  in_progress: {
    icon: Loader,
    color: 'text-blue-400',
    bgColor: 'bg-blue-500/10',
    text: 'In Progress'
  },
  failed: {
    icon: CheckCircle,
    color: 'text-red-400',
    bgColor: 'bg-red-500/10',
    text: 'Failed'
  }
}

export default function ResearchCard({ research }: ResearchCardProps) {
  const config = statusConfig[research.status]
  const StatusIcon = config.icon

  return (
    <div className="flex items-start space-x-4 p-4 bg-muted/30 rounded-md hover:bg-muted/50 transition-colors">
      <div className={`${config.bgColor} p-2 rounded-md`}>
        <StatusIcon className={`h-4 w-4 ${config.color} ${research.status === 'in_progress' ? 'animate-spin' : ''}`} />
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between">
          <h4 className="font-medium text-sm truncate">{research.title}</h4>
          <span className={`text-xs px-2 py-1 rounded-full ${config.bgColor} ${config.color} ml-2 flex-shrink-0`}>
            {config.text}
          </span>
        </div>

        <div className="flex flex-wrap gap-1 mt-2">
          {research.sources.map((source, index) => (
            <span
              key={index}
              className="text-xs px-2 py-1 bg-accent/10 text-accent rounded-md"
            >
              {source}
            </span>
          ))}
        </div>

        <div className="flex items-center mt-2 text-xs text-muted-foreground">
          <Clock className="h-3 w-3 mr-1" />
          {research.timestamp}
        </div>
      </div>
    </div>
  )
}
