import { Brain, FileText, Calendar } from 'lucide-react'

interface Skill {
  id: string
  title: string
  description: string
  sources: number
  created: string
}

interface SkillCardProps {
  skill: Skill
}

export default function SkillCard({ skill }: SkillCardProps) {
  return (
    <div className="card card-gold p-4 hover:shadow-glow transition-shadow cursor-pointer">
      <div className="flex items-start space-x-3">
        <div className="p-2 bg-accent/10 rounded-md flex-shrink-0">
          <Brain className="h-5 w-5 text-accent" />
        </div>

        <div className="flex-1 min-w-0">
          <h4 className="font-semibold text-sm mb-1 truncate">{skill.title}</h4>
          <p className="text-xs text-muted-foreground mb-3 line-clamp-2">
            {skill.description}
          </p>

          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <div className="flex items-center">
              <FileText className="h-3 w-3 mr-1" />
              {skill.sources} sources
            </div>

            <div className="flex items-center">
              <Calendar className="h-3 w-3 mr-1" />
              {new Date(skill.created).toLocaleDateString()}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
