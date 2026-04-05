// API service for communicating with Advanced Memory MCP backend
// This will connect to the MCP server via HTTP API endpoints

import axios, { AxiosInstance, AxiosResponse } from 'axios'

interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: string
  message?: string
}

interface LLMProvider {
  name: string
  type: 'local' | 'hosted'
  status: 'available' | 'unavailable' | 'configured' | 'not_configured'
  url: string
  description: string
  models?: string[]
}

interface ResearchResult {
  id: string
  title: string
  sources: string[]
  status: 'completed' | 'in_progress' | 'failed'
  timestamp: string
  content?: string
}


interface NoteResult {
  id: string
  title: string
  content: string
  tags: string[]
  created: string
  modified: string
  wordCount: number
  connections: number
  backlinks: number
  readingTime: number
  fileSize: string
  permalink?: string
}

interface SkillResult {
  id: string
  title: string
  description: string
  folder: string
  tags: string[]
  created: string
  modified: string
  content: string
  filePath: string
  sources: number
}

class ApiService {
  private client: AxiosInstance
  private _baseURL: string = ''

  getBaseUrl(): string {
    return this._baseURL
  }

  constructor() {
    // Configure axios client for ADN bridge server (stdio to HTTP bridge).
    // Override via VITE_API_URL (e.g. in Docker or .env).
    const baseURL =
      import.meta.env.VITE_API_URL || 'http://localhost:10705/api/v1'
    this.client = axios.create({
      baseURL,
      timeout: 12000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    this._baseURL = baseURL

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response: AxiosResponse) => response,
      (error) => {
        console.error('API Error:', error)
        return Promise.reject(error)
      }
    )
  }

  // Mock data for demo when backend is not available
  // Bridge and Service health check
  async getHealth(): Promise<ApiResponse> {
    try {
      // Detailed health check is at the root level of the bridge server
      // But we also have /api/v1/health which is what we use most often
      const response = await this.client.get('/health', {
        baseURL: this._baseURL.replace('/api/v1', '')
      })
      return { success: true, data: response.data }
    } catch (error) {
      console.error('Bridge health check failed:', error)
      return { success: false, error: 'Bridge server not responding' }
    }
  }

  // Fleet Discovery
  async getApps(): Promise<ApiResponse<any[]>> {
    try {
      const response = await this.client.get('/apps')
      return response.data
    } catch (error) {
      return { success: false, error: 'Failed to fetch discovered fleet' }
    }
  }



  // LLM Provider Management
  async getLLMProviders(): Promise<ApiResponse<LLMProvider[]>> {
    try {
      // For now, we only support Ollama as the local provider
      return {
        success: true,
        data: [
          {
            name: 'ollama',
            type: 'local',
            status: 'available',
            url: 'http://localhost:11434',
            description: 'Local models via Ollama',
            models: []
          }
        ]
      }
    } catch (error) {
      return { success: false, error: 'Failed to fetch LLM providers' }
    }
  }

  async getLLMModels(): Promise<ApiResponse<any[]>> {
    try {
      const response = await this.client.get('/llm/models')
      return response.data
    } catch (error) {
      return { success: false, error: 'Failed to fetch LLM models' }
    }
  }

  async selectLLMModel(provider: string, model: string): Promise<ApiResponse> {
    try {
      const response = await this.client.post('/llm/select', { provider, model })
      return response.data
    } catch (error) {
      return { success: false, error: 'Failed to select LLM model' }
    }
  }

  async loadLLMModel(provider: string, model: string): Promise<ApiResponse> {
    try {
      const response = await this.client.post('/llm/load', { provider, model })
      return response.data
    } catch (error) {
      return { success: false, error: 'Failed to load LLM model' }
    }
  }

  // Research Operations
  async startResearch(query: string, sources: string[]): Promise<ApiResponse<ResearchResult>> {
    try {
      const response = await this.client.post('/research/start', {
        query,
        sources,
        provider: 'auto'
      })
      return response.data
    } catch (error) {
      return { success: false, error: 'Failed to start research' }
    }
  }

  async getRecentResearch(): Promise<ApiResponse<ResearchResult[]>> {
    try {
      const response = await this.client.get('/research/recent')
      return response.data
    } catch (error) {
      return { success: false, error: 'Failed to fetch recent research' }
    }
  }

  // Skill Operations
  async generateSkill(topic: string, researchSources: string[]): Promise<ApiResponse<SkillResult>> {
    try {
      const response = await this.client.post('/skills/create', {
        topic,
        research_sources: researchSources,
        quality: 'comprehensive'
      })
      return response.data
    } catch (error) {
      return { success: false, error: 'Failed to create skill' }
    }
  }

  async getRecentSkills(): Promise<ApiResponse<SkillResult[]>> {
    try {
      const response = await this.client.get('/skills/recent')
      return response.data
    } catch (error) {
      return { success: false, error: 'Failed to fetch recent skills' }
    }
  }

  // Notes Management
  async getNotes(page: number = 1, limit: number = 50): Promise<ApiResponse<{ notes: NoteResult[], total: number, page: number, pages: number }>> {
    try {
      const response = await this.client.get(`/notes?page=${page}&limit=${limit}`)
      return response.data
    } catch (error) {
      return { success: false, error: 'Failed to fetch notes' }
    }
  }

  async getNote(noteId: string): Promise<ApiResponse<NoteResult>> {
    try {
      const response = await this.client.get(`/notes/${noteId}`)
      return response.data
    } catch (error) {
      return { success: false, error: 'Failed to fetch note' }
    }
  }

  async searchNotes(query: string, page: number = 1, limit: number = 50, tags?: string[]): Promise<ApiResponse<{ notes: NoteResult[], total: number, page: number, pages: number }>> {
    try {
      const params = new URLSearchParams({ query: query, page: page.toString(), limit: limit.toString() })
      if (tags && tags.length > 0) {
        params.append('tags', tags.join(','))
      }
      const response = await this.client.get(`/notes?${params}`)
      return response.data
    } catch (error) {
      return { success: false, error: 'Failed to search notes' }
    }
  }

  async createNote(note: { title: string, content: string, tags?: string[] }): Promise<ApiResponse<NoteResult>> {
    try {
      const response = await this.client.post('/notes', note)
      return response.data
    } catch (error) {
      return { success: false, error: 'Failed to create note' }
    }
  }

  async updateNote(noteId: string, updates: Partial<{ title: string, content: string, tags: string[] }>): Promise<ApiResponse<NoteResult>> {
    try {
      const response = await this.client.put(`/notes/${noteId}`, updates)
      return response.data
    } catch (error) {
      return { success: false, error: 'Failed to update note' }
    }
  }

  async deleteNote(noteId: string): Promise<ApiResponse> {
    try {
      const response = await this.client.delete(`/notes/${noteId}`)
      return response.data
    } catch (error) {
      return { success: false, error: 'Failed to delete note' }
    }
  }

  async getNoteConnections(noteId: string): Promise<ApiResponse<{ outgoing: any[], incoming: any[] }>> {
    try {
      const response = await this.client.get(`/notes/${noteId}/connections`)
      return response.data
    } catch (error) {
      return { success: false, error: 'Failed to fetch note connections' }
    }
  }

  async exportNote(noteId: string, format: string): Promise<ApiResponse<{ url: string }>> {
    try {
      const response = await this.client.post(`/notes/${noteId}/export`, { format })
      return response.data
    } catch (error) {
      return { success: false, error: 'Failed to export note' }
    }
  }

  // Skills Management
  async getSkills(folder?: string): Promise<ApiResponse<{ skills: SkillResult[], folders: string[] }>> {
    try {
      const params = folder ? `?folder=${folder}` : ''
      const response = await this.client.get(`/skills${params}`)
      return response.data
    } catch (error) {
      return { success: false, error: 'Failed to fetch skills' }
    }
  }

  async getSkill(skillId: string): Promise<ApiResponse<SkillResult>> {
    try {
      const response = await this.client.get(`/skills/${skillId}`)
      return response.data
    } catch (error) {
      return { success: false, error: 'Failed to fetch skill' }
    }
  }

  async createSkill(skill: { title: string, description: string, folder: string, tags?: string[], content: string }): Promise<ApiResponse<SkillResult>> {
    try {
      const response = await this.client.post('/skills', skill)
      return response.data
    } catch (error) {
      return { success: false, error: 'Failed to create skill' }
    }
  }

  async updateSkill(skillId: string, updates: Partial<{ title: string, description: string, tags: string[], content: string }>): Promise<ApiResponse<SkillResult>> {
    try {
      const response = await this.client.put(`/skills/${skillId}`, updates)
      return response.data
    } catch (error) {
      return { success: false, error: 'Failed to update skill' }
    }
  }

  async deleteSkill(skillId: string): Promise<ApiResponse> {
    try {
      const response = await this.client.delete(`/skills/${skillId}`)
      return response.data
    } catch (error) {
      return { success: false, error: 'Failed to delete skill' }
    }
  }

  async exportSkill(skillId: string, format: string): Promise<ApiResponse<{ url: string }>> {
    try {
      const response = await this.client.post(`/skills/${skillId}/export`, { format })
      return response.data
    } catch (error) {
      return { success: false, error: 'Failed to export skill' }
    }
  }

  async getSkillFolders(): Promise<ApiResponse<string[]>> {
    try {
      const response = await this.client.get('/skills/folders')
      return response.data
    } catch (error) {
      return { success: false, error: 'Failed to fetch skill folders' }
    }
  }

  // System Status
  async getSystemStatus(): Promise<ApiResponse> {
    try {
      const response = await this.client.get('/system/status')
      return response.data
    } catch (error) {
      return { success: false, error: 'Failed to fetch system status' }
    }
  }

  // Import / Export via adn_import_export MCP tool
  async importData(format: string, path: string, options?: Record<string, any>): Promise<ApiResponse> {
    try {
      const response = await this.client.post('/mcp/tools/adn_import_export', {
        arguments: { operation: 'import', format, path, options }
      })
      return response.data
    } catch (error) {
      return { success: false, error: 'Import failed' }
    }
  }

  async exportData(format: string, destination: string, options?: Record<string, any>): Promise<ApiResponse> {
    try {
      const response = await this.client.post('/mcp/tools/adn_import_export', {
        arguments: { operation: 'export', format, destination, options }
      })
      return response.data
    } catch (error) {
      return { success: false, error: 'Export failed' }
    }
  }

  // Chat — Standard LLM query (Personalities + Refining)
  async chatQuery(query: string, options: { personality?: string, model?: string, refine?: boolean } = {}): Promise<ApiResponse> {
    try {
      const response = await this.client.post('/chat', {
        query,
        ...options
      })
      return response.data
    } catch (error) {
      return { success: false, error: 'Chat query failed' }
    }
  }

  // Apps — health check proxy
  async checkAppHealth(port: number): Promise<ApiResponse> {
    try {
      const response = await this.client.get(`/apps/health/${port}`)
      return response.data
    } catch (error) {
      return { success: false, error: 'Health check failed' }
    }
  }

  // Semantic search (vector/RAG chunks) and note content for deep search UI
  async searchSemanticChunks(
    project: string,
    query: string,
    limit: number = 20
  ): Promise<ApiResponse<{ chunks: Array<{ entity_id: number; permalink: string | null; title: string; snippet: string; chunk_text: string; score: number }> }>> {
    try {
      const response = await this.client.post(`/${encodeURIComponent(project)}/search/semantic`, {
        query,
        limit
      })
      return response.data
    } catch (error) {
      return { success: false, error: 'Semantic search failed' }
    }
  }

  async getNoteContent(
    project: string,
    permalink: string
  ): Promise<ApiResponse<{ title: string; permalink: string | null; content: string }>> {
    try {
      const path = `${encodeURIComponent(project)}/knowledge/entities/${encodeURIComponent(permalink)}/content`
      const response = await this.client.get(path)
      return response.data
    } catch (error) {
      return { success: false, error: 'Failed to load note content' }
    }
  }

  // Project Management
  async getProjects(): Promise<ApiResponse<any[]>> {
    try {
      const response = await this.client.get('/projects')
      return response.data
    } catch (error) {
      return { success: false, error: 'Failed to fetch projects' }
    }
  }

  async createProject(name: string, path: string, description: string = '', setDefault: boolean = false): Promise<ApiResponse> {
    try {
      const response = await this.client.post('/projects', { name, path, description, set_default: setDefault })
      return response.data
    } catch (error) {
      return { success: false, error: 'Failed to create project' }
    }
  }

  async switchProject(name: string): Promise<ApiResponse> {
    try {
      const response = await this.client.post('/projects/switch', { name })
      return response.data
    } catch (error) {
      return { success: false, error: 'Failed to switch project' }
    }
  }

  async deleteProject(name: string): Promise<ApiResponse> {
    try {
      const response = await this.client.delete(`/projects/${name}`)
      return response.data
    } catch (error) {
      return { success: false, error: 'Failed to delete project' }
    }
  }

  // Graph Data (PointCloud)
  async getGraphData(): Promise<ApiResponse<{ nodes: any[], links: any[] }>> {
    try {
      const response = await this.client.get('/notes/graph')
      return response.data
    } catch (error) {
      return { success: false, error: 'Failed to fetch graph data' }
    }
  }

  // Batch Import
  async scanImportDir(path: string, months: number = 0): Promise<ApiResponse<any[]>> {
    try {
      const response = await this.client.post('/import/scan', { path, months })
      return response.data
    } catch (error) {
      return { success: false, error: 'Failed to scan directory' }
    }
  }

  async runBatchImport(files: string[], destinationFolder: string, project?: string): Promise<ApiResponse<any[]>> {
    try {
      const response = await this.client.post('/import/batch', {
        files,
        destination_folder: destinationFolder,
        project
      })
      return response.data
    } catch (error) {
      return { success: false, error: 'Batch import failed' }
    }
  }

  // Hardware and Model Management
  async detectHardware(): Promise<ApiResponse> {
    try {
      const response = await this.client.get('/hardware/detect')
      return response.data
    } catch (error) {
      return { success: false, error: 'Failed to detect hardware' }
    }
  }

  async optimizeModelParams(params: Record<string, any>): Promise<ApiResponse> {
    try {
      const response = await this.client.post('/model/optimize', params)
      return response.data
    } catch (error) {
      return { success: false, error: 'Failed to optimize model parameters' }
    }
  }

  // Test runner (requires ENABLE_WEBAPP_TESTS=1 on backend)
  async runTests(options?: { target?: string; timeout_seconds?: number; extra_args?: string[] }): Promise<
    ApiResponse<{ success: boolean; exit_code: number; stdout: string; stderr: string; duration_seconds: number }>
  > {
    try {
      const body = {
        target: options?.target ?? 'tests',
        timeout_seconds: options?.timeout_seconds ?? 300,
        extra_args: options?.extra_args ?? [],
      }
      const response = await this.client.post('/tests/run', body, { timeout: (body.timeout_seconds + 10) * 1000 })
      return response.data
    } catch (error: any) {
      const status = error?.response?.status
      const detail = error?.response?.data?.detail ?? error?.message ?? 'Test run failed'
      return { success: false, error: detail, data: status === 403 ? undefined : { success: false, exit_code: -1, stdout: '', stderr: String(detail), duration_seconds: 0 } }
    }
  }

  // Generic MCP tool caller (for skill creator, research, etc.)
  async callMCPTool(toolName: string, args: Record<string, any>): Promise<ApiResponse> {
    try {
      const response = await this.client.post(`/mcp/tools/${toolName}`, {
        arguments: args
      })
      return response.data
    } catch (error) {
      return { success: false, error: `Failed to call ${toolName}` }
    }
  }

}

// Export singleton instance
export const apiService = new ApiService()
export default apiService
