import {
  Bot,
  Calendar,
  Download,
  Plus,
  Save,
  Search,
  Share,
  Sparkles,
  Tag,
  Trash2,
  X,
} from "lucide-react";
import { useEffect, useState } from "react";
import { apiService } from "../../services/api";

interface Skill {
  id: string;
  title: string;
  description: string;
  folder: string;
  tags: string[];
  created: string;
  modified: string;
  content: string;
  filePath: string;
  modules?: SkillModule[];
}

interface SkillModule {
  name: string;
  content: string;
}

interface SkillsProps {
  selectedSkillId?: string;
  onSkillSelect?: (skillId: string) => void;
}

export default function Skills({ selectedSkillId, onSkillSelect }: SkillsProps) {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [filteredSkills, setFilteredSkills] = useState<Skill[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedSkill, setSelectedSkill] = useState<Skill | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [currentFolder, setCurrentFolder] = useState("all");
  const [availableFolders, setAvailableFolders] = useState<string[]>([
    "all",
    "cursor-skills",
    "windsurf-skills",
    "adn-skills",
    "antigravity-skills",
  ]);
  const [showCreateModal, setShowCreateModal] = useState(false);

  // Real skills from multiple IDE collections
  const mockSkills: Record<string, Skill[]> = {
    "cursor-skills": [
      {
        id: "1",
        title: "Create Rule",
        description:
          "Create Cursor rules for persistent AI guidance. Use when the user wants to create a rule, add coding standards, set up project conventions, configure file-specific patterns, create RULE.md files, or asks about .cursor/rules/ or AGENTS.md.",
        folder: "cursor-skills",
        tags: ["cursor", "rules", "guidance", "standards", "coding"],
        created: "2026-01-20 10:00:00",
        modified: "2026-01-20 10:00:00",
        content: `# Creating Cursor Rules

Create project rules in \`.cursor/rules/\` to provide persistent context for the AI agent.

## Gather Requirements

Before creating a rule, determine:
- **Purpose**: What should this rule enforce or teach?
- **Scope**: Should it always apply, or only for specific files?
- **File patterns**: If file-specific, which glob patterns?

## Rule File Format

Rules are \`.mdc\` files in \`.cursor/rules/\` with YAML frontmatter.

### Frontmatter Fields
- \`description\`: What the rule does (shown in rule picker)
- \`globs\`: File pattern - rule applies when matching files are open
- \`alwaysApply\`: If true, applies to every session`,
        filePath: "cursor-skills/create-rule/SKILL.md",
      },
      {
        id: "2",
        title: "Create Skill",
        description:
          "Guides users through creating effective Agent Skills for Cursor. Use when the user wants to create, write, or author a new skill, or asks about skill structure, best practices, or SKILL.md format.",
        folder: "cursor-skills",
        tags: ["cursor", "skills", "creation", "guidance", "agents"],
        created: "2026-01-20 10:00:00",
        modified: "2026-01-20 10:00:00",
        content: `# Creating Skills in Cursor

This skill guides you through creating effective Agent Skills for Cursor. Skills are markdown files that teach the agent how to perform specific tasks: reviewing PRs using team standards, generating commit messages in a preferred format, querying database schemas, or any specialized workflow.

## Before You Begin: Gather Requirements

Before creating a skill, gather essential information from the user about:

1. **Purpose and scope**: What specific task or workflow should this skill help with?
2. **Target location**: Should this be a personal skill (~/.cursor/skills/) or project skill (.cursor/skills/)?
3. **Trigger scenarios**: When should the agent automatically apply this skill?
4. **Key domain knowledge**: What specialized information does the agent need that it wouldn't already know?
5. **Output format preferences**: Are there specific templates, formats, or styles required?
6. **Existing patterns**: Are there existing examples or conventions to follow?

## Skill File Structure

Skills are stored as directories containing a \`SKILL.md\` file.

### Directory Layout
\`\`\`
skill-name/
â”œâ”€â”€ SKILL.md              # Required - main instructions
â”œâ”€â”€ reference.md          # Optional - detailed documentation
â”œâ”€â”€ examples.md           # Optional - usage examples
â””â”€â”€ scripts/              # Optional - utility scripts
\`\`\`

### File Format
\`\`\`markdown
---
name: "Skill Name"
description: "Brief description of what this skill does"
version: "1.0.0"
author: "Your Name"
tags: ["tag1", "tag2"]
---

# Skill Name

Your skill content here...
\`\`\`

## Best Practices

### Keep Skills Concise
- **Under 50 lines**: Skills should be concise and to the point
- **One concern per skill**: Split large skills into focused pieces
- **Actionable**: Write like clear internal docs
- **Concrete examples**: Ideally provide concrete examples of how to fix issues`,
        filePath: "cursor-skills/create-skill/SKILL.md",
      },
      {
        id: "3",
        title: "Update Cursor Settings",
        description:
          "Modify Cursor/VSCode user settings in settings.json. Use when the user wants to change editor settings, preferences, configuration, themes, font size, tab size, format on save, auto save, keybindings, or any settings.json values.",
        folder: "cursor-skills",
        tags: ["cursor", "settings", "configuration", "editor"],
        created: "2026-01-20 10:00:00",
        modified: "2026-01-20 10:00:00",
        content: `# Updating Cursor Settings

This skill helps modify Cursor/VSCode user settings in settings.json for various configuration needs.

## Common Settings to Modify

### Editor Settings
- \`editor.fontSize\`: Font size in pixels
- \`editor.tabSize\`: Number of spaces for a tab
- \`editor.insertSpaces\`: Whether to use spaces instead of tabs
- \`editor.formatOnSave\`: Automatically format files on save
- \`editor.formatOnType\`: Automatically format while typing

### Workspace Settings
- \`files.autoSave\`: Auto-save behavior ("off", "afterDelay", "onFocusChange", "onWindowChange")
- \`files.trimTrailingWhitespace\`: Remove trailing whitespace
- \`files.insertFinalNewline\`: Add final newline to files

### UI Settings
- \`workbench.colorTheme\`: Color theme
- \`workbench.iconTheme\`: Icon theme
- \`window.zoomLevel\`: Window zoom level

## Usage Examples

### Change Font Size
\`\`\`json
{
  "editor.fontSize": 14
}
\`\`\`

### Enable Format on Save
\`\`\`json
{
  "editor.formatOnSave": true
}
\`\`\`

### Set Tab Size
\`\`\`json
{
  "editor.tabSize": 2,
  "editor.insertSpaces": true
}
\`\`\``,
        filePath: "cursor-skills/update-cursor-settings/SKILL.md",
      },
      {
        id: "4",
        title: "Create Subagent",
        description:
          "Create custom subagents for specialized AI tasks. Use when the user wants to create a subagent, set up task-specific agents, configure code reviewers, debuggers, or domain-specific assistants with custom prompts.",
        folder: "cursor-skills",
        tags: ["cursor", "subagents", "ai", "tasks", "specialized"],
        created: "2026-01-20 10:00:00",
        modified: "2026-01-20 10:00:00",
        content: `# Creating Subagents in Cursor

This skill guides you through creating custom subagents for specialized AI tasks in Cursor.

## What are Subagents?

Subagents are specialized AI assistants that handle specific types of tasks. They can be configured with custom prompts, tools, and behaviors to excel at particular domains.

## Types of Subagents

### Code Review Subagent
Specializes in reviewing code for:
- Security vulnerabilities
- Performance issues
- Code quality standards
- Best practices compliance

### Debugging Subagent
Focuses on:
- Error analysis and diagnosis
- Debugging strategies
- Root cause identification
- Fix recommendations

### Documentation Subagent
Handles:
- Code documentation generation
- README file creation
- API documentation
- User guide writing

## Creating a Subagent

### Step 1: Define the Scope
Determine what specific tasks the subagent should handle and what domain knowledge it needs.

### Step 2: Craft the Prompt
Write a clear, specific prompt that defines:
- The subagent's role and expertise
- The types of tasks it handles
- The expected output format
- Any specific guidelines or constraints

### Step 3: Configure Tools
Set up the appropriate tools and integrations for the subagent's domain.

### Step 4: Test and Refine
Test the subagent with various scenarios and refine the prompt and configuration as needed.

## Example Subagent Prompt

\`\`\`
You are an expert code reviewer specializing in React applications. Your task is to review React components for:

1. Performance optimizations
2. Best practices compliance
3. Security vulnerabilities
4. Accessibility standards
5. Code maintainability

For each issue found, provide:
- A clear description of the problem
- The specific line(s) of code affected
- A suggested fix with code example
- The severity level (Critical, High, Medium, Low)

Focus on actionable feedback that helps improve code quality.
\`\`\``,
        filePath: "cursor-skills/create-subagent/SKILL.md",
      },
    ],
    "windsurf-skills": [
      {
        id: "5",
        title: "MCP Server Developer",
        description:
          "Expert in developing Model Context Protocol servers with FastMCP. Covers server architecture, tool implementation, resource management, and integration patterns.",
        folder: "windsurf-skills",
        tags: ["mcp", "server", "development", "fastmcp", "api"],
        created: "2026-01-20 10:00:00",
        modified: "2026-01-20 10:00:00",
        content: `# MCP Server Development

Expert guidance for developing Model Context Protocol servers using FastMCP framework.

## Core Concepts

### MCP Architecture
- **Server**: Provides tools, resources, and prompts to MCP clients
- **Client**: Applications that connect to MCP servers (IDEs, chat apps)
- **Protocol**: JSON-RPC 2.0 based communication over stdio
- **Transport**: Bidirectional communication channel

### FastMCP Framework
FastMCP is a high-performance, easy-to-use framework for building MCP servers in Python.

## Server Structure

### Basic Server Setup
\`\`\`python
from fastmcp import FastMCP

app = FastMCP("My Server")

@app.tool()
def my_tool(param: str) -> str:
    """Tool description"""
    return f"Processed: {param}"

if __name__ == "__main__":
    app.run()
\`\`\`

### Tool Implementation
Tools are functions that can be called by MCP clients:

\`\`\`python
@app.tool()
def search_files(query: str, directory: str = ".") -> list[str]:
    """Search for files containing the query"""
    # Implementation here
    pass
\`\`\`

### Resource Management
Resources provide access to data:

\`\`\`python
@app.resource("file://{path}")
def read_file(path: str) -> str:
    """Read file content"""
    with open(path, 'r') as f:
        return f.read()
\`\`\`

## Best Practices

### Error Handling
Always handle errors gracefully and provide meaningful error messages:

\`\`\`python
@app.tool()
def safe_operation(param: str) -> dict:
    """Perform operation with error handling"""
    try:
        result = perform_operation(param)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
\`\`\`

### Type Hints
Use proper type hints for better documentation and validation:

\`\`\`python
from typing import List, Optional
from pydantic import BaseModel

class SearchResult(BaseModel):
    file_path: str
    line_number: int
    content: str

@app.tool()
def advanced_search(query: str, file_pattern: Optional[str] = None) -> List[SearchResult]:
    # Implementation
    pass
\`\`\``,
        filePath: "windsurf-skills/mcp-server-developer/SKILL.md",
      },
      {
        id: "6",
        title: "Presentation Design Expert",
        description:
          "Specialist in creating compelling presentations with visual storytelling, slide design, and audience engagement techniques.",
        folder: "windsurf-skills",
        tags: ["presentation", "design", "visual", "storytelling"],
        created: "2026-01-20 10:00:00",
        modified: "2026-01-20 10:00:00",
        content: `# Presentation Design Expert

Specialist in creating compelling presentations with visual storytelling, slide design, and audience engagement techniques.

## Core Principles

### Story First
Every great presentation tells a story. Focus on:
- Clear narrative structure
- Audience journey mapping
- Emotional connection
- Memorable takeaways

### Visual Hierarchy
Guide the audience's attention with:
- Strategic use of whitespace
- Size and color contrast
- Typography scales
- Visual flow patterns

## Slide Design Fundamentals

### Layout Principles
- **Rule of Thirds**: Divide slides into 3x3 grid for optimal content placement
- **White Space**: Use breathing room to reduce cognitive load
- **Alignment**: Consistent alignment creates visual harmony
- **Proximity**: Group related elements together

### Typography
- **Font Selection**: 1-2 complementary fonts maximum
- **Size Hierarchy**: 4-6 different sizes for clear information hierarchy
- **Readability**: Ensure 24pt minimum for body text
- **Contrast**: High contrast ratios for accessibility

### Color Psychology
- **Brand Colors**: Consistent use of organizational colors
- **Accent Colors**: Use sparingly for emphasis and calls-to-action
- **Cultural Context**: Consider color meanings across cultures
- **Accessibility**: Ensure sufficient contrast ratios

## Content Strategy

### Opening Strong
- Hook the audience in the first 30 seconds
- State the purpose and value proposition
- Set expectations for what's to come

### Building the Body
- One main point per slide
- Use visuals to support, not replace, content
- Include relevant data and examples
- Maintain consistent pacing

### Closing with Impact
- Summarize key takeaways
- End with a strong call-to-action
- Leave the audience with a clear next step

## Technical Excellence

### Tool Mastery
- **PowerPoint/Google Slides**: Advanced features and shortcuts
- **Keynote**: Mac-specific design capabilities
- **Canva**: Quick design for simpler presentations
- **Adobe Creative Suite**: Advanced design and animation

### Animation and Transitions
- **Purposeful Motion**: Every animation should serve a purpose
- **Timing**: Consistent timing for professional feel
- **Builds**: Progressive disclosure of information
- **Entrance/Exit**: Smooth transitions between sections

## Audience Engagement

### Interactive Elements
- **Questions**: Strategic pauses for audience input
- **Polls**: Real-time feedback during presentation
- **Activities**: Brief exercises or discussions
- **Stories**: Personal anecdotes and case studies

### Delivery Techniques
- **Eye Contact**: Connect with different audience segments
- **Voice Modulation**: Vary pace, volume, and tone
- **Body Language**: Confident, open posture
- **Energy Management**: Maintain consistent enthusiasm

## Measurement and Improvement

### Feedback Collection
- **Post-Presentation Surveys**: Gather audience insights
- **Peer Review**: Get feedback from colleagues
- **Self-Assessment**: Record and review your own presentations
- **Analytics**: Track engagement metrics when possible

### Continuous Learning
- **Study Masters**: Analyze presentations by recognized experts
- **Practice Regularly**: Hone skills through frequent presentation
- **Stay Current**: Follow presentation design trends and best practices
- **Experiment**: Try new techniques and technologies`,
        filePath: "windsurf-skills/presentation-design-expert/SKILL.md",
      },
    ],
    "adn-skills": [
      {
        id: "7",
        title: "AI Debate Dominator",
        description:
          "Expert in structured debates, argumentation techniques, and persuasive communication across various topics and domains.",
        folder: "adn-skills",
        tags: ["debate", "argumentation", "persuasion", "communication"],
        created: "2026-01-20 10:00:00",
        modified: "2026-01-20 10:00:00",
        content: `# AI Debate Dominator

Expert in structured debates, argumentation techniques, and persuasive communication across various topics and domains.

## Debate Fundamentals

### Argument Structure
Every strong argument contains:
- **Claim**: Clear statement of position
- **Evidence**: Facts, data, or examples supporting the claim
- **Warrant**: Explanation of how evidence supports the claim
- **Backing**: Additional support for the warrant
- **Qualifier**: Limits or conditions of the claim

### Evidence Types
- **Factual**: Statistical data, research findings, historical records
- **Testimonial**: Expert opinions, witness accounts, authoritative statements
- **Analogical**: Comparisons between similar situations
- **Hypothetical**: Logical scenarios or thought experiments

## Debate Formats

### Lincoln-Douglas
- One-on-one debate format
- Values and criteria based argumentation
- Cross-examination periods
- Focus on philosophical and value-based topics

### Policy Debate
- Team-based format (2 vs 2)
- Affirmative/Negative positions
- Plan-based argumentation
- Focus on policy implementation and effects

### Parliamentary Debate
- Multi-team format
- Government/Opposition roles
- Points of Information (POI) system
- Fast-paced, spontaneous argumentation

## Argumentation Techniques

### Building Strong Cases
- **Primacy**: Present strongest arguments first
- **Recency**: End with memorable points
- **Signposting**: Clearly indicate argument structure
- **Transitions**: Smooth connections between ideas

### Refutation Strategies
- **Direct Refutation**: Attack opponent's core claims
- **Counterarguments**: Present alternative interpretations
- **Undermining**: Question opponent's evidence credibility
- **Turn**: Use opponent's argument against them

### Fallacy Recognition
Common logical fallacies to avoid:
- **Ad Hominem**: Attacking the person instead of arguments
- **Straw Man**: Misrepresenting opponent's position
- **False Dichotomy**: Presenting only two options when more exist
- **Appeal to Emotion**: Manipulating emotions instead of logic

## Communication Skills

### Rhetorical Devices
- **Ethos**: Establish credibility and trustworthiness
- **Pathos**: Appeal to emotions and values
- **Logos**: Use logical reasoning and evidence
- **Kairos**: Timing and context awareness

### Delivery Techniques
- **Pacing**: Vary speech rate for emphasis
- **Volume**: Use vocal dynamics effectively
- **Pausing**: Strategic silences for impact
- **Emphasis**: Stress key words and phrases

## Topic Analysis

### Research Methodology
- **Source Evaluation**: Assess credibility and bias
- **Evidence Synthesis**: Combine multiple sources effectively
- **Counter-Research**: Anticipate opposing viewpoints
- **Trend Analysis**: Identify emerging patterns and developments

### Case Building
- **Advocacy**: Clearly state and justify your position
- **Disadvantages**: Address potential downsides of your position
- **Counterplans**: Alternative solutions to the problem
- **Impact Calculus**: Weigh relative importance of arguments

## Debate Psychology

### Mental Preparation
- **Confidence Building**: Thorough preparation reduces anxiety
- **Visualization**: Mental rehearsal of successful debates
- **Stress Management**: Techniques for staying calm under pressure
- **Recovery**: Learning from losses and setbacks

### Audience Awareness
- **Adaptation**: Adjust arguments based on audience knowledge
- **Persuasion**: Understand different persuasion techniques
- **Cultural Sensitivity**: Respect diverse perspectives and backgrounds
- **Ethical Communication**: Maintain integrity and respect in discourse

## Advanced Techniques

### Strategic Thinking
- **Game Theory**: Anticipate opponent moves and responses
- **Risk Assessment**: Evaluate potential argument vulnerabilities
- **Positioning**: Strategic placement of arguments for maximum impact
- **Flexibility**: Adapt strategies based on debate flow

### Meta-Debate Skills
- **Flow Reading**: Track complex argument interactions
- **Speed Analysis**: Quick evaluation of argument strength
- **Position Shifting**: Adjust positions based on new information
- **Synthesis**: Combine multiple arguments into cohesive narratives

## Practice and Improvement

### Skill Development
- **Regular Practice**: Frequent debate participation
- **Recording Analysis**: Review and critique own performances
- **Mentorship**: Learn from experienced debaters
- **Reading**: Study argumentation theory and examples

### Continuous Learning
- **Stay Current**: Follow current events and emerging topics
- **Technique Refinement**: Regularly update and improve methods
- **Feedback Integration**: Use constructive criticism for growth
- **Goal Setting**: Establish clear improvement objectives`,
        filePath: "adn-skills/ai-debate-dominator/SKILL.md",
      },
    ],
    "antigravity-skills": [
      {
        id: "8",
        title: "Full Stack Developer",
        description:
          "Comprehensive full-stack development expertise covering frontend, backend, databases, DevOps, and modern development practices.",
        folder: "antigravity-skills",
        tags: ["fullstack", "development", "frontend", "backend", "devops"],
        created: "2026-01-20 10:00:00",
        modified: "2026-01-20 10:00:00",
        content: `# Full Stack Developer

Comprehensive full-stack development expertise covering frontend, backend, databases, DevOps, and modern development practices.

## Technology Stack

### Frontend Technologies
- **React/Next.js**: Component-based UI development
- **TypeScript**: Type-safe JavaScript development
- **Tailwind CSS**: Utility-first CSS framework
- **Vue.js/Nuxt.js**: Progressive JavaScript framework
- **Svelte/SvelteKit**: Reactive UI framework

### Backend Technologies
- **Node.js/Express**: JavaScript runtime and web framework
- **Python/FastAPI**: High-performance Python web framework
- **Go/Gin**: Efficient compiled language for backend services
- **Rust/Axum**: Memory-safe systems programming
- **Java/Spring Boot**: Enterprise-grade Java applications

### Database Technologies
- **PostgreSQL**: Advanced open-source relational database
- **MongoDB**: Document-based NoSQL database
- **Redis**: In-memory data structure store
- **MySQL**: Popular relational database
- **SQLite**: Embedded database for development

## Development Practices

### Code Quality
- **Type Safety**: Comprehensive type checking and validation
- **Testing**: Unit, integration, and end-to-end test coverage
- **Code Review**: Peer review processes and standards
- **Documentation**: API docs, code comments, and user guides
- **Linting**: Automated code quality checks

### Architecture Patterns
- **MVC**: Model-View-Controller separation
- **MVVM**: Model-View-ViewModel for reactive UIs
- **Microservices**: Distributed system architecture
- **Serverless**: Event-driven compute services
- **Monolithic**: Traditional single-application architecture

### Security Best Practices
- **Authentication**: JWT, OAuth, session management
- **Authorization**: Role-based and permission-based access
- **Data Validation**: Input sanitization and validation
- **HTTPS/TLS**: Encrypted communication
- **CORS**: Cross-origin resource sharing configuration

## DevOps and Deployment

### Containerization
- **Docker**: Container platform for application packaging
- **Docker Compose**: Multi-container application management
- **Kubernetes**: Container orchestration platform
- **Podman**: Daemonless container engine

### CI/CD Pipelines
- **GitHub Actions**: Cloud-based CI/CD platform
- **GitLab CI**: Integrated DevOps platform
- **Jenkins**: Extensible automation server
- **CircleCI**: Cloud-based CI/CD service

### Cloud Platforms
- **AWS**: Amazon Web Services ecosystem
- **Google Cloud**: GCP services and tools
- **Azure**: Microsoft cloud platform
- **Vercel/Netlify**: Frontend deployment platforms

## Performance Optimization

### Frontend Optimization
- **Code Splitting**: Dynamic imports and lazy loading
- **Bundle Analysis**: Optimizing bundle sizes
- **Caching**: Browser caching strategies
- **CDN**: Content delivery networks
- **Image Optimization**: Format selection and compression

### Backend Optimization
- **Database Indexing**: Query performance optimization
- **Caching**: Redis, Memcached, in-memory caching
- **Load Balancing**: Traffic distribution
- **Horizontal Scaling**: Application scaling strategies
- **Profiling**: Performance monitoring and analysis

## API Design

### RESTful APIs
- **HTTP Methods**: GET, POST, PUT, DELETE, PATCH
- **Status Codes**: Appropriate HTTP response codes
- **Resource Design**: RESTful resource modeling
- **Versioning**: API versioning strategies
- **Documentation**: OpenAPI/Swagger specifications

### GraphQL APIs
- **Schema Design**: Type definitions and resolvers
- **Query Optimization**: N+1 problem prevention
- **Caching**: Query result caching
- **Subscriptions**: Real-time data updates
- **Security**: Query complexity limits

## Testing Strategies

### Testing Pyramid
- **Unit Tests**: Individual function/component testing
- **Integration Tests**: Component interaction testing
- **End-to-End Tests**: Full application workflow testing
- **Contract Tests**: API contract validation
- **Performance Tests**: Load and stress testing

### Testing Tools
- **Jest**: JavaScript testing framework
- **React Testing Library**: React component testing
- **Cypress**: End-to-end testing framework
- **Playwright**: Cross-browser testing
- **Postman/Newman**: API testing

## Modern Development Workflow

### Version Control
- **Git**: Distributed version control system
- **Branching Strategies**: GitFlow, trunk-based development
- **Pull Requests**: Code review and merge processes
- **Conventional Commits**: Standardized commit messages

### Project Management
- **Agile**: Iterative development methodology
- **Scrum**: Framework for agile project management
- **Kanban**: Visual project management method
- **Issue Tracking**: Jira, GitHub Issues, Linear

## Soft Skills

### Communication
- **Technical Writing**: Documentation and blog posts
- **Code Reviews**: Providing constructive feedback
- **Team Collaboration**: Working effectively in teams
- **Client Interaction**: Requirements gathering and feedback

### Problem Solving
- **Debugging**: Systematic issue identification and resolution
- **Algorithm Design**: Efficient solution development
- **System Design**: Scalable architecture planning
- **Technical Debt**: Balancing speed and quality

## Continuous Learning

### Staying Current
- **Technology Trends**: Following industry developments
- **Open Source**: Contributing to community projects
- **Conferences**: Attending tech conferences and meetups
- **Online Learning**: Courses, tutorials, and documentation

### Skill Development
- **Side Projects**: Personal project development
- **Code Challenges**: Algorithm and coding practice
- **Mentorship**: Teaching and learning from others
- **Blogging**: Sharing knowledge and experiences`,
        filePath: "antigravity-skills/full-stack-developer/SKILL.md",
      },
    ],
  };

  const loadSkills = async () => {
    setIsLoading(true);
    try {
      const folderParam = currentFolder === "all" ? undefined : currentFolder;
      const response = await apiService.getSkills(folderParam);
      if (response.success && response.data?.skills) {
        const skillsData = response.data.skills;
        setSkills(skillsData);
        setFilteredSkills(skillsData);

        if (response.data.folders && response.data.folders.length > 0) {
          setAvailableFolders((prev) => {
            const fromApi = response.data!.folders as string[];
            if (prev[0] === "all") return ["all", ...fromApi];
            return fromApi;
          });
        }
        setIsLoading(false);
        return;
      }

      console.warn("Bridge server not available - showing mock skills for demo");
      setTimeout(() => {
        const folderSkills =
          currentFolder === "all"
            ? ([] as Skill[]).concat(...Object.values(mockSkills))
            : mockSkills[currentFolder] || [];
        setSkills(folderSkills);
        setFilteredSkills(folderSkills);
        setIsLoading(false);
      }, 500);
    } catch (error) {
      console.error("Failed to load skills from API, showing mock data:", error);
      setTimeout(() => {
        const folderSkills =
          currentFolder === "all"
            ? ([] as Skill[]).concat(...Object.values(mockSkills))
            : mockSkills[currentFolder] || [];
        setSkills(folderSkills);
        setFilteredSkills(folderSkills);
        setIsLoading(false);
      }, 500);
    }
  };

  useEffect(() => {
    loadSkills();
  }, [currentFolder]);

  useEffect(() => {
    // Filter skills based on search query
    if (searchQuery.trim() === "") {
      setFilteredSkills(skills);
    } else {
      const filtered = skills.filter(
        (skill) =>
          skill.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          skill.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
          skill.tags.some((tag) => tag.toLowerCase().includes(searchQuery.toLowerCase())),
      );
      setFilteredSkills(filtered);
    }
  }, [searchQuery, skills]);

  useEffect(() => {
    // Select skill if selectedSkillId is provided
    if (selectedSkillId && skills.length > 0) {
      const skill = skills.find((s) => s.id === selectedSkillId);
      if (skill) {
        setSelectedSkill(skill);
      }
    }
  }, [selectedSkillId, skills]);

  const handleSkillSelect = (skill: Skill) => {
    setSelectedSkill(skill);
    onSkillSelect?.(skill.id);
  };

  const handleCreateSkill = () => {
    setShowCreateModal(true);
  };

  const handleCloseCreateModal = () => {
    setShowCreateModal(false);
  };

  return (
    <div className="flex h-full bg-gray-900 text-white">
      {/* Sidebar */}
      <div className="w-80 bg-gray-800 border-r border-gray-700 flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gold-400">Skills</h2>
            <button
              onClick={handleCreateSkill}
              className="p-2 bg-gold-600 hover:bg-gold-700 rounded-lg transition-colors"
              title="Create new skill"
            >
              <Plus className="w-5 h-5" />
            </button>
          </div>

          {/* Folder selector */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-300 mb-2">Skill Collection</label>
            <select
              value={currentFolder}
              onChange={(e) => setCurrentFolder(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-gold-500 focus:border-transparent"
            >
              {availableFolders.map((folder) => (
                <option key={folder} value={folder}>
                  {folder === "all"
                    ? "All collections"
                    : folder.replace(/-/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}
                </option>
              ))}
            </select>
          </div>

          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search skills..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-gold-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Skills List */}
        <div className="flex-1 overflow-y-auto">
          {isLoading ? (
            <div className="p-4 text-center text-gray-400">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gold-500 mx-auto mb-2"></div>
              Loading skills...
            </div>
          ) : filteredSkills.length === 0 ? (
            <div className="p-4 text-center text-gray-400">
              <Bot className="w-12 h-12 mx-auto mb-2 text-gray-500" />
              {searchQuery ? "No skills match your search" : "No skills available"}
            </div>
          ) : (
            <div className="p-2">
              {filteredSkills.map((skill) => (
                <div
                  key={skill.id}
                  onClick={() => handleSkillSelect(skill)}
                  className={`p-3 mb-2 rounded-lg cursor-pointer transition-colors border ${
                    selectedSkill?.id === skill.id
                      ? "bg-gold-600 border-gold-500"
                      : "bg-gray-700 border-gray-600 hover:bg-gray-650"
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <h3 className="font-medium text-white truncate">{skill.title}</h3>
                      <p className="text-sm text-gray-300 mt-1 line-clamp-2">{skill.description}</p>
                      {skill.tags.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-2">
                          {skill.tags.slice(0, 3).map((tag) => (
                            <span
                              key={tag}
                              className="px-2 py-1 text-xs bg-gray-600 text-gray-300 rounded-full"
                            >
                              {tag}
                            </span>
                          ))}
                          {skill.tags.length > 3 && (
                            <span className="px-2 py-1 text-xs bg-gray-600 text-gray-300 rounded-full">
                              +{skill.tags.length - 3}
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                    <div className="ml-2 flex-shrink-0">
                      <Sparkles className="w-5 h-5 text-gold-400" />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {selectedSkill ? (
          <SkillViewer skill={selectedSkill} onClose={() => setSelectedSkill(null)} />
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center text-gray-400">
              <Bot className="w-16 h-16 mx-auto mb-4 text-gray-500" />
              <h3 className="text-xl font-medium mb-2">Select a Skill</h3>
              <p>Choose a skill from the sidebar to view its details</p>
            </div>
          </div>
        )}
      </div>

      {/* Create Skill Modal */}
      {showCreateModal && <CreateSkillModal onClose={handleCloseCreateModal} />}
    </div>
  );
}

// Skill Viewer Component
function SkillViewer({ skill, onClose }: { skill: Skill; onClose: () => void }) {
  return (
    <div className="flex-1 flex flex-col bg-gray-900">
      {/* Header */}
      <div className="p-6 border-b border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
            <div>
              <h1 className="text-2xl font-bold text-white">{skill.title}</h1>
              <p className="text-gray-400 mt-1">{skill.description}</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button className="p-2 hover:bg-gray-700 rounded-lg transition-colors">
              <Download className="w-5 h-5" />
            </button>
            <button className="p-2 hover:bg-gray-700 rounded-lg transition-colors">
              <Share className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Metadata */}
        <div className="flex items-center space-x-6 mt-4 text-sm text-gray-400">
          <div className="flex items-center space-x-1">
            <Tag className="w-4 h-4" />
            <span>{skill.folder}</span>
          </div>
          <div className="flex items-center space-x-1">
            <Calendar className="w-4 h-4" />
            <span>Created {new Date(skill.created).toLocaleDateString()}</span>
          </div>
          {skill.tags.length > 0 && (
            <div className="flex items-center space-x-2">
              {skill.tags.map((tag) => (
                <span
                  key={tag}
                  className="px-2 py-1 bg-gray-700 text-gray-300 rounded-full text-xs"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="prose prose-invert max-w-none">
          <pre className="whitespace-pre-wrap text-gray-300 leading-relaxed">{skill.content}</pre>
        </div>

        {/* Modules */}
        {skill.modules && skill.modules.length > 0 && (
          <div className="mt-8">
            <h2 className="text-xl font-bold text-white mb-4">Modules</h2>
            <div className="space-y-4">
              {skill.modules.map((module, index) => (
                <div key={index} className="bg-gray-800 rounded-lg p-4">
                  <h3 className="text-lg font-medium text-gold-400 mb-2">{module.name}</h3>
                  <pre className="whitespace-pre-wrap text-gray-300 text-sm">{module.content}</pre>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// Create Skill Modal Component
function CreateSkillModal({ onClose }: { onClose: () => void }) {
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    folder: "cursor-skills",
    tags: "",
    overview: "",
    whenToUse: "",
  });
  const [modules, setModules] = useState<SkillModule[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [selectedLLM, setSelectedLLM] = useState("");
  const [llmError, setLlmError] = useState("");

  const addModule = () => {
    setModules([...modules, { name: "", content: "" }]);
  };

  const removeModule = (index: number) => {
    setModules(modules.filter((_, i) => i !== index));
  };

  const updateModule = (index: number, field: keyof SkillModule, value: string) => {
    const updatedModules = [...modules];
    if (updatedModules[index]) {
      updatedModules[index][field] = value;
      setModules(updatedModules);
    }
  };

  const generateSkillContent = async () => {
    if (!formData.title || !selectedLLM) return;

    setIsGenerating(true);
    setLlmError("");

    try {
      // This would integrate with local LLM APIs (Ollama, LM Studio)
      // For now, generate basic content
      const generatedContent = `# ${formData.title}

${formData.overview || "This skill provides specialized guidance and automation for specific development tasks."}

## When to Use

${formData.whenToUse || "Apply this skill when working on related development tasks."}

## Key Features

- Specialized guidance for ${formData.title.toLowerCase()}
- Best practices and patterns
- Automation and tooling recommendations`;

      setFormData((prev) => ({ ...prev, overview: generatedContent }));
    } catch (error) {
      setLlmError("Failed to generate content with LLM");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSubmit = async () => {
    // This would create the skill file and save it
    // For now, just close the modal
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-gray-800 rounded-lg w-full max-w-4xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="p-6 border-b border-gray-700">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-white">Create New Skill</h2>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
          {/* LLM Generation Section */}
          <div className="mb-6 p-4 bg-gray-700 rounded-lg">
            <h3 className="text-lg font-medium text-white mb-3">Generate with AI</h3>
            <div className="flex space-x-4">
              <select
                value={selectedLLM}
                onChange={(e) => setSelectedLLM(e.target.value)}
                className="px-3 py-2 bg-gray-600 border border-gray-500 rounded-lg text-white focus:ring-2 focus:ring-gold-500"
              >
                <option value="">Select LLM</option>
                <option value="ollama">Ollama (Local)</option>
                <option value="lmstudio">LM Studio (Local)</option>
              </select>
              <button
                onClick={generateSkillContent}
                disabled={isGenerating || !selectedLLM || !formData.title}
                className="px-4 py-2 bg-gold-600 hover:bg-gold-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg transition-colors flex items-center space-x-2"
              >
                <Sparkles className="w-4 h-4" />
                <span>{isGenerating ? "Generating..." : "Generate Content"}</span>
              </button>
            </div>
            {llmError && <p className="text-red-400 text-sm mt-2">{llmError}</p>}
          </div>

          {/* Form Tabs */}
          <div className="mb-6">
            <div className="flex space-x-1">
              <button className="px-4 py-2 bg-gold-600 text-white rounded-lg">Overview</button>
              <button className="px-4 py-2 bg-gray-700 text-gray-300 hover:bg-gray-600 rounded-lg">
                Modules
              </button>
            </div>
          </div>

          {/* Overview Tab */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Title</label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData((prev) => ({ ...prev, title: e.target.value }))}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-gold-500 focus:border-transparent"
                placeholder="Skill title"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Description</label>
              <input
                type="text"
                value={formData.description}
                onChange={(e) => setFormData((prev) => ({ ...prev, description: e.target.value }))}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-gold-500 focus:border-transparent"
                placeholder="Brief description"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Folder</label>
              <select
                value={formData.folder}
                onChange={(e) => setFormData((prev) => ({ ...prev, folder: e.target.value }))}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-gold-500 focus:border-transparent"
              >
                <option value="cursor-skills">Cursor Skills</option>
                <option value="windsurf-skills">Windsurf Skills</option>
                <option value="adn-skills">ADN Skills</option>
                <option value="antigravity-skills">Antigravity Skills</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Tags (comma-separated)
              </label>
              <input
                type="text"
                value={formData.tags}
                onChange={(e) => setFormData((prev) => ({ ...prev, tags: e.target.value }))}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-gold-500 focus:border-transparent"
                placeholder="tag1, tag2, tag3"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Overview Content
              </label>
              <textarea
                value={formData.overview}
                onChange={(e) => setFormData((prev) => ({ ...prev, overview: e.target.value }))}
                rows={10}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-gold-500 focus:border-transparent font-mono text-sm"
                placeholder="Skill content in markdown format"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">When to Use</label>
              <textarea
                value={formData.whenToUse}
                onChange={(e) => setFormData((prev) => ({ ...prev, whenToUse: e.target.value }))}
                rows={3}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-gold-500 focus:border-transparent"
                placeholder="Describe when this skill should be applied"
              />
            </div>
          </div>

          {/* Modules Tab - Hidden for now */}
          <div className="hidden">
            <div className="space-y-4">
              {modules.map((module, index) => (
                <div key={index} className="p-4 bg-gray-700 rounded-lg">
                  <div className="flex items-center justify-between mb-3">
                    <input
                      type="text"
                      value={module.name}
                      onChange={(e) => updateModule(index, "name", e.target.value)}
                      placeholder="Module name"
                      className="flex-1 px-3 py-2 bg-gray-600 border border-gray-500 rounded-lg text-white mr-3"
                    />
                    <button
                      onClick={() => removeModule(index)}
                      className="p-2 text-red-400 hover:bg-red-900 rounded-lg"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                  <textarea
                    value={module.content}
                    onChange={(e) => updateModule(index, "content", e.target.value)}
                    rows={5}
                    placeholder="Module content"
                    className="w-full px-3 py-2 bg-gray-600 border border-gray-500 rounded-lg text-white font-mono text-sm"
                  />
                </div>
              ))}
              <button
                onClick={addModule}
                className="w-full py-2 border-2 border-dashed border-gray-600 rounded-lg text-gray-400 hover:border-gold-500 hover:text-gold-400 transition-colors flex items-center justify-center space-x-2"
              >
                <Plus className="w-4 h-4" />
                <span>Add Module</span>
              </button>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-700 flex justify-end space-x-3">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-gray-300 rounded-lg transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            className="px-4 py-2 bg-gold-600 hover:bg-gold-700 text-white rounded-lg transition-colors flex items-center space-x-2"
          >
            <Save className="w-4 h-4" />
            <span>Create Skill</span>
          </button>
        </div>
      </div>
    </div>
  );
}
