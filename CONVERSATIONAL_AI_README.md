# Conversational AI Extension for Advanced Memory MCP

[![Status: Planning](https://img.shields.io/badge/status-planning-orange.svg)]()
[![Timeline: 8 weeks](https://img.shields.io/badge/timeline-8%20weeks-blue.svg)]()
[![Priority: Low](https://img.shields.io/badge/priority-low-green.svg)]()

## Overview

This extension transforms the ADN webapp from a basic CRUD interface into a **Claude-like conversational AI assistant** that leverages the full power of the ADN knowledge graph and MCP tool ecosystem through natural language interaction.

**Key Innovation**: Self-reinforcing knowledge loop where conversations enhance the knowledge graph and the knowledge graph improves conversation quality.

## 💰 **Cost-Free AI Experience**

**No API Costs Required!** If you already have Ollama running locally, this extension provides full conversational AI capabilities completely free of charge. No expensive cloud API tokens needed - everything runs on your own hardware.

## Strategic Rationale

### Why Conversational AI for ADN?

**Current ADN Webapp Limitations:**
- Basic CRUD operations only
- Manual navigation required
- No natural language interaction
- Limited tool orchestration
- No conversation persistence

**Conversational AI Benefits:**
- **Natural Interaction**: Ask questions in plain English instead of clicking through menus
- **Tool Orchestration**: Automatic discovery and use of ADN's 25+ MCP tools
- **Context Awareness**: Relevant knowledge automatically injected from ADN graph
- **Memory Persistence**: Conversations become searchable knowledge in ADN
- **Research Acceleration**: AI-assisted exploration of knowledge connections
- **Cost-Free**: Runs entirely on local Ollama - no API fees or subscriptions required

### ADN-Native Approach

**Why Not Use Existing Frameworks?**
- Open WebUI would overshadow ADN's knowledge management focus
- Agent Cloud lacks MCP-native integration
- Custom implementation preserves ADN's unique value proposition

**ADN Strengths Leveraged:**
- Knowledge graph for conversation memory
- Existing MCP tool ecosystem
- Research-driven knowledge synthesis
- Zettelkasten-based note system

## Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    React Webapp                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Chat Interface                        │    │
│  │  • Message History & Streaming                     │    │
│  │  • Tool Call Visualization                         │    │
│  │  • Conversation Management                        │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              ADN Integration                       │    │
│  │  • Knowledge Graph Browser                        │    │
│  │  │  Note Linking & References                     │    │
│  │  • Research Context Injection                     │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                                 │
                    ┌────────────────────┐
                    │  Bridge Server     │
                    │  (Enhanced)        │
                    │  ┌─────────────┐   │
                    │  │ Chat API    │   │
                    │  │ Endpoints   │   │
                    │  └─────────────┘   │
                    │  ┌─────────────┐   │
                    │  │ Tool Proxy  │   │
                    │  │ & Registry │   │
                    │  └─────────────┘   │
                    │  ┌─────────────┐   │
                    │  │ Context     │   │
                    │  │ Injection   │   │
                    │  └─────────────┘   │
                    └────────────────────┘
                                 │
                    ┌────────────────────┐
                    │  ADN MCP Server    │
                    │  (Existing)        │
                    │  ┌─────────────┐   │
                    │  │ 25+ Tools   │   │
                    │  │ Portmanteaus│   │
                    │  └─────────────┘   │
                    │  ┌─────────────┐   │
                    │  │ Knowledge   │   │
                    │  │ Operations  │   │
                    │  └─────────────┘   │
                    └────────────────────┘
                                 │
                    ┌────────────────────┐
                    │ Conversation Memory│
                    │ (ADN Knowledge     │
                    │  Graph Storage)    │
                    └────────────────────┘
```

### Component Details

**Frontend (React/TypeScript):**
- Modern chat interface with streaming responses
- Real-time tool call visualization
- Conversation management and search
- Seamless ADN knowledge graph integration

**Bridge Server (Enhanced):**
- Chat completions API with tool orchestration
- WebSocket streaming support
- Dynamic MCP tool discovery and conversion
- Context injection from ADN knowledge graph

**ADN MCP Server (Existing):**
- 25+ portmanteau tools for knowledge operations
- Full-text search and relation mapping
- Research and skill synthesis capabilities

**Ollama Integration:**
- Tool-use enabled models (qwen2.5, llama3.2, mistral-nemo)
- Function calling and streaming responses
- Automatic model management and switching

## User Experience Transformation

### Before: Manual CRUD Operations
```
User wants to research quantum computing:
1. Navigate to Research page
2. Click "New Research"
3. Select sources (Web, arXiv, GitHub)
4. Enter query manually
5. Wait for results
6. Read through findings
7. Manually create notes from results
8. Link notes to existing knowledge
```

### After: Natural Conversation
```
User: "Help me research the latest developments in quantum computing"

Assistant: "I'd be happy to help you research quantum computing. I can see you have several related notes already. Let me search for recent developments and connect them to your existing knowledge..."

[Tool calls visualized in real-time]
- Web search: "quantum computing 2024 developments"
- arXiv search: "quantum computing recent papers"
- Context injection from existing notes

Assistant: "Based on your existing research on quantum algorithms and the latest developments, here are the key findings..."
```

## Technical Implementation Plan

### Phase 1: Core Infrastructure (Weeks 1-2)

#### 1.1 Ollama Tool-Use Integration
**Goal:** Enable function calling with ADN tool orchestration

**Requirements:**
- Ollama v0.4.0+ with native tool support
- Tool-enabled models: `qwen2.5:7b`, `llama3.2:3b`, `mistral-nemo:12b`
- MCP tool schema conversion to Ollama format

**Deliverables:**
- `OllamaService` class with tool calling support
- MCP-to-Ollama tool schema conversion
- Model validation and switching logic

#### 1.2 Enhanced Bridge Server
**Goal:** Add conversation management and streaming capabilities

**New Endpoints:**
```
POST /api/v1/chat/completions      # Main chat endpoint
GET  /api/v1/conversations         # List conversations
POST /api/v1/conversations         # Create conversation
GET  /api/v1/conversations/:id     # Get conversation
WebSocket /api/v1/chat/stream      # Streaming responses
GET  /api/v1/tools/discover        # Dynamic tool discovery
```

**Features:**
- Chat completions with tool orchestration
- WebSocket streaming for real-time responses
- Conversation persistence coordination
- Context injection from ADN knowledge graph

#### 1.3 Tool Registry System
**Goal:** Dynamic MCP tool discovery and schema conversion

**Capabilities:**
- Automatic tool schema extraction from ADN MCP server
- Conversion to Ollama-compatible format
- Tool filtering by conversation context
- Caching for performance optimization

### Phase 2: Conversation Memory (Weeks 3-4)

#### 2.1 ADN Conversation Storage
**Goal:** Use ADN knowledge graph for persistent conversations

**Storage Schema:**
```typescript
interface Conversation {
  id: string
  title: string
  created: Date
  updated: Date
  messages: ConversationMessage[]
  context: {
    relevant_notes: string[]
    active_tools: string[]
    knowledge_injection: boolean
  }
}

interface ConversationMessage {
  id: string
  role: 'user' | 'assistant' | 'system' | 'tool'
  content: string
  timestamp: Date
  tool_calls?: ToolCall[]
  tool_results?: ToolResult[]
}
```

**Storage Strategy:**
- Conversations as ADN notes with special metadata
- Message threading using ADN's relation system
- Searchable conversation history
- Context preservation across sessions

#### 2.2 Context Injection System
**Goal:** Automatically inject relevant ADN knowledge during conversations

**Algorithm:**
1. **Keyword Analysis**: Extract keywords from user messages
2. **Knowledge Search**: Query ADN knowledge graph for relevant notes
3. **Relevance Scoring**: Weight by recency, connectivity, and content similarity
4. **Context Injection**: Insert top-N relevant contexts as system messages

**Example:**
```
User: "Tell me about quantum computing research"

System Injection:
"Relevant knowledge from your notes:
- Quantum algorithms paper (2024-01-15)
- IBM Quantum experience notes (2024-02-20)
- Current research trends (2024-03-01)"

Assistant: [Response using injected context]
```

### Phase 3: Chat Interface (Weeks 5-6)

#### 3.1 React Chat Components
**Goal:** Modern streaming chat interface with ADN integration

**Components:**
- `ChatInterface`: Main chat container with message history
- `MessageBubble`: Individual messages with role-based styling
- `StreamingMessage`: Real-time response rendering
- `ToolCallDisplay`: Visual tool execution feedback
- `ConversationManager`: Conversation creation, listing, and search

**Features:**
- Markdown rendering for rich content
- Streaming text responses with typing indicators
- Tool call visualization during execution
- Conversation persistence and retrieval
- ADN knowledge graph linking

#### 3.2 Tool Orchestration UI
**Goal:** Visual feedback for tool use and execution

**Capabilities:**
- Real-time tool call display
- Parameter visualization
- Execution status indicators
- Result preview and modification
- Error recovery options
- Tool chaining visualization

### Phase 4: Advanced Features (Weeks 7-8)

#### 4.1 Multi-Agent Conversations
**Goal:** Allow multiple AI personas in single conversation

**Features:**
- Agent switching commands (`@research-agent`, `@coding-assistant`)
- Context handoff between agents
- Agent-specific tool access
- Shared conversation memory

#### 4.2 Conversation Templates
**Goal:** Reusable conversation patterns for common workflows

**Templates:**
- Research assistant mode
- Code review mode
- Knowledge synthesis mode
- Creative writing mode
- Technical documentation mode

#### 4.3 Voice Integration (Optional)
**Goal:** Voice input/output capabilities

**Features:**
- Speech-to-text for input
- Text-to-speech for responses
- Voice activity detection
- Audio message storage in ADN

## ADN Tool Integration Strategy

### Leveraging ADN Capabilities for Development

**Knowledge Management (`adn_knowledge`):**
- Store conversation designs and research findings
- Track implementation progress and decisions
- Create interconnected notes for different components
- Search existing ADN knowledge during development

**Research Operations (`adn_research`):**
- Web search for conversational AI patterns and implementations
- GitHub exploration for similar open-source projects
- Academic research on tool use and conversation memory
- Document ingestion of research papers and specifications

**Project Management (`adn_project`):**
- Create dedicated project for extension development
- Track milestones and phase completion
- Monitor development velocity and blockers
- Coordinate with existing ADN development workflow

**Development Workflow:**
1. **Planning:** Use `adn_research` to gather requirements and patterns
2. **Design:** Store designs as `adn_knowledge` notes with relationships
3. **Implementation:** Track progress with status updates
4. **Testing:** Document findings and iterate using ADN search
5. **Deployment:** Preserve all work in ADN knowledge graph

## Success Metrics

### Functional Metrics
- ✅ Natural language conversations with ADN tools
- ✅ Automatic tool discovery and orchestration
- ✅ Conversation persistence in ADN knowledge graph
- ✅ Context injection improves response quality
- ✅ Real-time tool execution visualization

### Performance Targets
- **Response Time:** < 3 seconds for simple queries
- **Tool Execution:** < 10 seconds completion
- **Memory Usage:** < 500MB for webapp
- **Concurrent Conversations:** Support 10+ simultaneous

### Quality Metrics
- **Tool Call Accuracy:** > 90%
- **Context Relevance:** > 80%
- **User Satisfaction:** > 4/5 rating

## Risk Assessment & Mitigation

### Technical Risks
- **Ollama Tool Support:** Requires specific models with function calling
- **MCP Schema Complexity:** Complex tools may break schema conversion
- **Memory Performance:** Large conversation histories impact performance

### Mitigation Strategies
- Model validation with fallbacks
- Progressive tool loading (start with simple tools)
- Conversation pagination and archiving
- Performance monitoring and optimization

## Business Value & Impact

### User Experience Transformation
**Before:** Manual navigation through CRUD interfaces
**After:** Natural language interaction with intelligent assistance

### Knowledge Graph Enhancement
**Self-Reinforcing Loop:**
```
Conversations → Knowledge Graph → Better Conversations
```

- Research acceleration through context-aware responses
- Knowledge discovery via conversational exploration
- Automatic connection of related concepts

### Competitive Advantages
- **ADN-Native:** Preserves unique knowledge management focus
- **Tool Integration:** Full MCP ecosystem access via conversation
- **Memory Persistence:** Conversations become searchable knowledge
- **Context Awareness:** Relevant information automatically injected

## Development Prerequisites

### 🎯 **Only Ollama Required (FREE & Local)**

**The beauty of this extension:** Everything runs locally on your hardware - no cloud costs!

### Technical Requirements
- **Ollama:** v0.4.0+ with tool support *(FREE - just install once)*
- **Models:** qwen2.5:7b, llama3.2:3b, mistral-nemo:12b *(FREE - download once)*
- **Node.js:** 18+ for React development
- **Python:** 3.11+ for ADN MCP server

### ADN System Status
- MCP server running and accessible
- Bridge server operational
- Webapp functional
- Knowledge graph populated with test data

### 💡 **Cost Comparison**
- **This Extension:** $0 (one-time Ollama install)
- **Cloud AI APIs:** $20-50/month minimum
- **Proprietary AI Tools:** $10-200/month
- **ROI:** Immediate - saves hundreds annually while keeping everything private and local

## Getting Started

### Phase 1 Development Setup
```bash
# 1. Install Ollama tool-enabled models
ollama pull qwen2.5:7b
ollama pull llama3.2:3b

# 2. Verify ADN MCP server
advanced-memory status

# 3. Start development environment (RECOMMENDED: clean startup)
cd ..
.\run-webapp-clean.bat  # Kills zombies, starts on port 17770

# Alternative: Direct webapp startup
cd webapp
npm install
npm run dev  # Runs on http://localhost:17770 (strict port)
```

### Testing Tool Integration
```bash
# First check if webapp is running on port 17770
.\check-webapp-port.ps1

# Test basic tool calling
curl -X POST http://localhost:8001/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Search for notes about quantum computing"}],
    "tools_enabled": true
  }'

# Graceful shutdown of entire ADN system
curl -X POST http://localhost:8001/api/v1/system/graceful-exit \
  -H "Content-Type: application/json" \
  -d '{"reason": "Testing shutdown", "force": false}'
```

### Port Management & System Control
- **Webapp Port:** `17770` (strict, no hopping)
- **Bridge Server:** `8001`
- **Startup Service:** `8002`
- **Auto-Start Service:** `8003`

**System Control Endpoints:**
```
POST /api/v1/system/graceful-exit
- Gracefully shuts down all ADN processes
- Body: {"reason": "string", "force": boolean}
- Returns: {"success": true, "message": "shutdown initiated"}
```

**Process Management:**
- Always use `.\run-webapp-clean.bat` to kill existing processes before restart
- Use `.\check-webapp-port.ps1` to diagnose port conflicts
- Use `.\shutdown-adn.ps1` or `.\shutdown-adn.bat` for remote graceful shutdown
- Never allow port hopping - fix conflicts instead

## Documentation & Resources

- **[Full Technical Plan](./CONVERSATIONAL_AI_EXTENSION_PLAN.md)** - Comprehensive implementation details
- **[ADN Content Note](./zettelkasten/2026-01-23-conversational-ai-extension-plan.md)** - Knowledge graph entry
- **[ADN Tools Reference](./docs/tools-reference.md)** - Available MCP tool documentation
- **[FastMCP Documentation](https://fastmcp.com)** - MCP protocol reference

## Next Steps

1. **Begin Phase 1:** Set up Ollama tool-use environment
2. **Create Project:** Use `adn_project` to track development
3. **Research Patterns:** Use `adn_research` for implementation patterns
4. **Prototype Chat:** Build basic chat interface with tool calling
5. **Test Integration:** Verify ADN knowledge graph conversation storage

---

*This extension represents ADN's evolution from knowledge management tool to intelligent conversational assistant, creating a self-reinforcing loop where human-AI interaction continuously enhances the knowledge base.*
