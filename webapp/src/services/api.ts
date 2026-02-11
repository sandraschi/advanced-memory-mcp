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

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response: AxiosResponse) => response,
      (error) => {
        console.error('API Error:', error)
        if (error.response?.status === 404) {
          // Backend not available - return mock data for demo
          console.warn('Backend not available, using mock data')
          return Promise.resolve({
            data: this.getMockResponse(error.config.url)
          })
        }
        return Promise.reject(error)
      }
    )
  }

  // Mock data for demo when backend is not available
  private getMockResponse(url?: string): any {
    if (url?.includes('/llm/providers')) {
      return {
        success: true,
        data: [
          {
            name: 'ollama',
            type: 'local',
            status: 'available',
            url: 'http://localhost:11434',
            description: 'Local models via Ollama',
            models: ['llama3:8b', 'llama3:70b', 'codellama:13b']
          },
          {
            name: 'lmstudio',
            type: 'local',
            status: 'unavailable',
            url: 'http://localhost:1234',
            description: 'Local models via LM Studio (OpenAI-compatible)',
            models: []
          },
          {
            name: 'openai',
            type: 'hosted',
            status: 'configured',
            url: 'https://api.openai.com/v1',
            description: 'Hosted models via OpenAI API',
            models: ['gpt-4o', 'gpt-4-turbo', 'gpt-3.5-turbo']
          }
        ]
      }
    }

    if (url?.includes('/research/recent')) {
      return {
        success: true,
        data: [
          {
            id: '1',
            title: 'Brain Tumor Treatment Breakthroughs 2024',
            sources: ['Web (15 articles)', 'arXiv (8 papers)', 'Clinical Trials'],
            status: 'completed',
            timestamp: '2026-01-20 14:31:40',
            content: 'Research shows promising results with immunotherapy combinations...'
          },
          {
            id: '2',
            title: 'Quantum Machine Learning Algorithms',
            sources: ['GitHub (12 repos)', 'arXiv (6 papers)', 'Web'],
            status: 'in_progress',
            timestamp: '2026-01-20 14:45:22',
            content: 'Analyzing latest quantum computing approaches...'
          }
        ]
      }
    }

    if (url?.includes('/skills/recent')) {
      return {
        success: true,
        data: [
          {
            id: '1',
            title: 'Brain Tumor Treatment Expert',
            description: 'Comprehensive knowledge of current glioblastoma treatments, clinical trials, and emerging therapies',
            sources: 31,
            created: '2026-01-20 14:31:40',
            content: 'Expert knowledge covering surgical resection, radiation therapy, chemotherapy, and immunotherapy approaches...'
          },
          {
            id: '2',
            title: 'Neural Network Architect',
            description: 'Deep learning model design, optimization techniques, and implementation patterns',
            sources: 28,
            created: '2026-01-20 14:15:33',
            content: 'Comprehensive understanding of neural network architectures, training methodologies, and deployment strategies...'
          }
        ]
      }
    }

    return { success: false, error: 'Backend not available' }
  }

  // LLM Provider Management
  async getLLMProviders(): Promise<ApiResponse<LLMProvider[]>> {
    try {
      const response = await this.client.get('/llm/providers')
      return response.data
    } catch (error) {
      return { success: false, error: 'Failed to fetch LLM providers' }
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

  async searchNotes(query: string, tags?: string[]): Promise<ApiResponse<NoteResult[]>> {
    try {
      const params = new URLSearchParams({ q: query })
      if (tags && tags.length > 0) {
        params.append('tags', tags.join(','))
      }
      const response = await this.client.get(`/notes/search?${params}`)
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
      return {
        success: true,
        data: {
          llm_provider: 'ollama',
          llm_model: 'llama3:8b',
          knowledge_base_size: 1247,
          research_apis_status: 'available'
        }
      }
    }
  }

}

// Export singleton instance
export const apiService = new ApiService()
export default apiService
