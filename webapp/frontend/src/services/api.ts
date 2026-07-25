// API service for communicating with Advanced Memory MCP backend
// This will connect to the MCP server via HTTP API endpoints

import axios, { type AxiosInstance, type AxiosResponse } from "axios";

import { getApiBaseUrl } from "../config/apiBase";

/** Client wait for full vault scan or FTS + LanceDB reindex (20 minutes). */
const VAULT_LONG_OPERATION_TIMEOUT_MS = 1_200_000;

interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

interface LLMProvider {
  name: string;
  type: "local" | "hosted";
  status: "available" | "unavailable" | "configured" | "not_configured";
  url: string;
  description: string;
  models?: string[];
}

interface ResearchResult {
  id: string;
  title: string;
  sources: string[];
  status: "completed" | "in_progress" | "failed";
  timestamp: string;
  content?: string;
}

interface NoteResult {
  id: string;
  title: string;
  content: string;
  tags: string[];
  created: string;
  modified: string;
  wordCount: number;
  connections: number;
  backlinks: number;
  readingTime: number;
  fileSize: string;
  permalink?: string;
}

/** Search hits may expose tags as an array, a JSON string, a bare string, or omit them. */
function normalizeNoteTags(raw: unknown): string[] {
  if (Array.isArray(raw)) {
    return raw.map((t) => String(t)).filter((t) => t.length > 0);
  }
  if (typeof raw === "string") {
    const s = raw.trim();
    if (!s) {
      return [];
    }
    if (s.startsWith("[") || s.startsWith("{")) {
      try {
        const p = JSON.parse(s) as unknown;
        if (Array.isArray(p)) {
          return p.map((x) => String(x)).filter((t) => t.length > 0);
        }
      } catch {
        /* treat as single tag */
      }
    }
    return [s];
  }
  return [];
}

interface SkillResult {
  id: string;
  title: string;
  description: string;
  folder: string;
  tags: string[];
  created: string;
  modified: string;
  content: string;
  filePath: string;
  sources: number;
}

class ApiService {
  private client: AxiosInstance;
  private _baseURL = "";
  public activeProject = "main";

  getBaseUrl(): string {
    return this._baseURL;
  }

  constructor() {
    // FastAPI under /api/v1. Dev default is same-origin + Vite proxy to port 10705.
    const baseURL = getApiBaseUrl();
    this.client = axios.create({
      baseURL,
      timeout: 12000,
      headers: {
        "Content-Type": "application/json",
      },
    });

    this._baseURL = baseURL;

    // Reject failed requests without logging — callers surface errors in UI; logging every 4xx/5xx was console spam.
    this.client.interceptors.response.use(
      (response: AxiosResponse) => response,
      (error) => Promise.reject(error),
    );
  }

  // Mock data for demo when backend is not available
  // Bridge and Service health check
  async getHealth(): Promise<ApiResponse> {
    try {
      const response = await this.client.get("/health");
      return { success: true, data: response.data };
    } catch {
      return { success: false, error: "Bridge server not responding" };
    }
  }

  // Fleet Discovery
  async getApps(): Promise<ApiResponse<any[]>> {
    try {
      const response = await this.client.get("/apps");
      return response.data;
    } catch (error) {
      return { success: false, error: "Failed to fetch discovered fleet" };
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
            name: "ollama",
            type: "local",
            status: "available",
            url: "http://localhost:11434",
            description: "Local models via Ollama",
            models: [],
          },
        ],
      };
    } catch (error) {
      return { success: false, error: "Failed to fetch LLM providers" };
    }
  }

  async getLLMModels(): Promise<ApiResponse<any[]>> {
    try {
      const response = await this.client.get("/llm/models");
      return response.data;
    } catch (error) {
      return { success: false, error: "Failed to fetch LLM models" };
    }
  }

  async selectLLMModel(provider: string, model: string): Promise<ApiResponse> {
    try {
      const response = await this.client.post("/llm/select", { provider, model });
      return response.data;
    } catch (error) {
      return { success: false, error: "Failed to select LLM model" };
    }
  }

  async loadLLMModel(provider: string, model: string): Promise<ApiResponse> {
    try {
      const response = await this.client.post("/llm/load", { provider, model });
      return response.data;
    } catch (error) {
      return { success: false, error: "Failed to load LLM model" };
    }
  }

  // Research Operations
  async startResearch(query: string, sources: string[]): Promise<ApiResponse<ResearchResult>> {
    try {
      const response = await this.client.post("/research/start", {
        query,
        sources,
        provider: "auto",
      });
      return response.data;
    } catch (error) {
      return { success: false, error: "Failed to start research" };
    }
  }

  async getRecentResearch(): Promise<ApiResponse<ResearchResult[]>> {
    return { success: true, data: [] };
  }

  // Skill Operations
  async generateSkill(topic: string, researchSources: string[]): Promise<ApiResponse<SkillResult>> {
    try {
      const response = await this.client.post("/skills/create", {
        topic,
        research_sources: researchSources,
        quality: "comprehensive",
      });
      return response.data;
    } catch (error) {
      return { success: false, error: "Failed to create skill" };
    }
  }

  async getRecentSkills(): Promise<ApiResponse<SkillResult[]>> {
    try {
      return { success: true, data: [] };
    } catch (error) {
      return { success: false, error: "Failed to fetch recent skills" };
    }
  }

  // Notes/Entities Management
  async getNotes(
    page = 1,
    limit = 50,
  ): Promise<ApiResponse<{ notes: NoteResult[]; total: number; page: number; pages: number }>> {
    try {
      return await this.searchNotes("", page, limit);
    } catch (error) {
      return { success: false, error: "Failed to fetch notes" };
    }
  }

  async getNote(noteId: string): Promise<ApiResponse<NoteResult>> {
    try {
      // Use the project-scoped knowledge content endpoint
      const path = `/${encodeURIComponent(this.activeProject)}/knowledge/entities/${encodeURIComponent(noteId)}/content`;
      const response = await this.client.get(path);
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: "Failed to fetch note" };
    }
  }

  async searchNotes(
    query: string,
    page = 1,
    limit = 50,
    tags?: string[],
  ): Promise<ApiResponse<{ notes: NoteResult[]; total: number; page: number; pages: number }>> {
    try {
      const q = (query || "").trim();
      // Backend returns nothing when all criteria are null; glob lists indexed notes.
      const body: Record<string, any> = q ? { text: q } : { permalink_match: "*" };
      if (tags && tags.length > 0) body.tags = tags;

      const response = await this.client.post(
        `/${encodeURIComponent(this.activeProject)}/search/?page=${page}&page_size=${limit}`,
        body,
      );
      const results = response.data.results || [];

      const notes = results.map((r: any) => ({
        id: r.permalink || r.file_path,
        title: r.title,
        content: r.content || r.content_snippet || "",
        created: r.created_at || new Date().toISOString(),
        modified: r.updated_at || new Date().toISOString(),
        tags: normalizeNoteTags(r.metadata?.tags),
        wordCount: 0,
        connections: 0,
      }));

      const total = response.data.total_results || 0;
      const pages = Math.ceil(total / limit) || 1;

      return { success: true, data: { notes, total, page, pages } };
    } catch (error) {
      return { success: false, error: "Failed to search notes" };
    }
  }

  async createNote(note: { title: string; content: string; tags?: string[] }): Promise<
    ApiResponse<NoteResult>
  > {
    try {
      const response = await this.client.post("/notes", note);
      return response.data;
    } catch (error) {
      return { success: false, error: "Failed to create note" };
    }
  }

  async updateNote(
    noteId: string,
    updates: Partial<{ title: string; content: string; tags: string[] }>,
  ): Promise<ApiResponse<NoteResult>> {
    try {
      const response = await this.client.put(`/notes/${noteId}`, updates);
      return response.data;
    } catch (error) {
      return { success: false, error: "Failed to update note" };
    }
  }

  async deleteNote(noteId: string): Promise<ApiResponse> {
    try {
      const response = await this.client.delete(`/notes/${noteId}`);
      return response.data;
    } catch (error) {
      return { success: false, error: "Failed to delete note" };
    }
  }

  async getNoteConnections(
    noteId: string,
  ): Promise<ApiResponse<{ outgoing: any[]; incoming: any[] }>> {
    try {
      const response = await this.client.get(`/notes/${noteId}/connections`);
      return response.data;
    } catch (error) {
      return { success: false, error: "Failed to fetch note connections" };
    }
  }

  async exportNote(noteId: string, format: string): Promise<ApiResponse<{ url: string }>> {
    try {
      const response = await this.client.post(`/notes/${noteId}/export`, { format });
      return response.data;
    } catch (error) {
      return { success: false, error: "Failed to export note" };
    }
  }

  // Skills Management
  async getSkills(
    folder?: string,
  ): Promise<ApiResponse<{ skills: SkillResult[]; folders: string[] }>> {
    try {
      const params = folder ? `?folder=${folder}` : "";
      const response = await this.client.get(
        `/${encodeURIComponent(this.activeProject)}/skills${params}`,
      );
      const skills = response.data.skills || response.data || [];
      return { success: true, data: { skills, folders: [] } };
    } catch (error) {
      return { success: false, error: "Failed to fetch skills" };
    }
  }

  async getSkill(skillId: string): Promise<ApiResponse<SkillResult>> {
    try {
      const response = await this.client.get(`/skills/${skillId}`);
      return response.data;
    } catch (error) {
      return { success: false, error: "Failed to fetch skill" };
    }
  }

  async createSkill(skill: {
    title: string;
    description: string;
    folder: string;
    tags?: string[];
    content: string;
  }): Promise<ApiResponse<SkillResult>> {
    try {
      const response = await this.client.post("/skills", skill);
      return response.data;
    } catch (error) {
      return { success: false, error: "Failed to create skill" };
    }
  }

  async updateSkill(
    skillId: string,
    updates: Partial<{ title: string; description: string; tags: string[]; content: string }>,
  ): Promise<ApiResponse<SkillResult>> {
    try {
      const response = await this.client.put(`/skills/${skillId}`, updates);
      return response.data;
    } catch (error) {
      return { success: false, error: "Failed to update skill" };
    }
  }

  async deleteSkill(skillId: string): Promise<ApiResponse> {
    try {
      const response = await this.client.delete(`/skills/${skillId}`);
      return response.data;
    } catch (error) {
      return { success: false, error: "Failed to delete skill" };
    }
  }

  async exportSkill(skillId: string, format: string): Promise<ApiResponse<{ url: string }>> {
    try {
      const response = await this.client.post(`/skills/${skillId}/export`, { format });
      return response.data;
    } catch (error) {
      return { success: false, error: "Failed to export skill" };
    }
  }

  async getSkillFolders(): Promise<ApiResponse<string[]>> {
    try {
      const response = await this.client.get("/skills/folders");
      return response.data;
    } catch (error) {
      return { success: false, error: "Failed to fetch skill folders" };
    }
  }

  // System Status
  async getSystemStatus(): Promise<ApiResponse> {
    try {
      const response = await this.client.get("/health");
      return {
        success: true,
        data: { status: response.data?.status || "online", load: "idle", uptime: 9999 },
      };
    } catch (error) {
      // Return mocked system status on failure
      return { success: true, data: { status: "offline", load: "idle", uptime: 0 } };
    }
  }

  // Import / Export via adn_import_export MCP tool
  async importData(
    format: string,
    path: string,
    options?: Record<string, any>,
  ): Promise<ApiResponse> {
    try {
      const response = await this.client.post("/mcp/tools/adn_import_export", {
        arguments: { operation: "import", format, path, options },
      });
      return response.data;
    } catch (error) {
      return { success: false, error: "Import failed" };
    }
  }

  async exportData(
    format: string,
    destination: string,
    options?: Record<string, any>,
  ): Promise<ApiResponse> {
    try {
      const response = await this.client.post("/mcp/tools/adn_import_export", {
        arguments: { operation: "export", format, destination, options },
      });
      return response.data;
    } catch (error) {
      return { success: false, error: "Export failed" };
    }
  }

  // Chat — Standard LLM query (Personalities + Refining)
  async chatQuery(
    query: string,
    options: { personality?: string; model?: string; refine?: boolean } = {},
  ): Promise<ApiResponse> {
    try {
      const response = await this.client.post("/chat", {
        query,
        ...options,
      });
      return response.data;
    } catch (error) {
      return { success: false, error: "Chat query failed" };
    }
  }

  // Apps — health check proxy
  async checkAppHealth(port: number): Promise<ApiResponse> {
    try {
      const response = await this.client.get(`/apps/health/${port}`);
      return response.data;
    } catch (error) {
      return { success: false, error: "Health check failed" };
    }
  }

  // Semantic search (vector/RAG chunks) and note content for deep search UI
  async searchSemanticChunks(
    project: string,
    query: string,
    limit = 20,
  ): Promise<
    ApiResponse<{
      chunks: Array<{
        entity_id: number;
        permalink: string | null;
        title: string;
        snippet: string;
        chunk_text: string;
        score: number;
      }>;
    }>
  > {
    try {
      const response = await this.client.post(`/${encodeURIComponent(project)}/search/semantic`, {
        query,
        limit,
      });
      return response.data;
    } catch (error) {
      return { success: false, error: "Semantic search failed" };
    }
  }

  async getNoteContent(
    project: string,
    permalink: string,
  ): Promise<ApiResponse<{ title: string; permalink: string | null; content: string }>> {
    try {
      const path = `/${encodeURIComponent(project)}/knowledge/entities/${encodeURIComponent(permalink)}/content`;
      const response = await this.client.get(path);
      return response.data;
    } catch (error) {
      return { success: false, error: "Failed to load note content" };
    }
  }

  async getProjects(): Promise<ApiResponse<any[]>> {
    try {
      const response = await this.client.get("/projects");
      const body = response.data;
      if (!body || typeof body !== "object") {
        return { success: false, error: "Invalid projects response" };
      }
      const raw = (body as { projects?: unknown; default_project?: unknown }).projects;
      if (!Array.isArray(raw)) {
        return { success: false, error: "Missing projects list in API response" };
      }
      const defaultProject =
        typeof (body as { default_project?: unknown }).default_project === "string"
          ? (body as { default_project: string }).default_project
          : undefined;
      if (defaultProject) {
        this.activeProject = defaultProject;
      }
      const projects = raw.map((p: any) => ({
        name: String(p.name ?? ""),
        path: String(p.path ?? ""),
        is_default: Boolean(p.is_default) || p.name === defaultProject,
        status: p.is_active ? "READY" : "INACTIVE",
      }));
      return { success: true, data: projects };
    } catch (error) {
      return { success: false, error: "Failed to fetch projects" };
    }
  }

  /** Recent entities/observations for the active project (FastAPI `GET /{project}/memory/recent`). */
  async getMemoryRecent(options?: {
    timeframe?: string;
    page?: number;
    pageSize?: number;
    depth?: number;
  }): Promise<
    ApiResponse<{
      results: Array<{ primary_result?: Record<string, unknown> }>;
      metadata?: Record<string, unknown>;
    }>
  > {
    try {
      const project = encodeURIComponent(this.activeProject);
      const timeframe = options?.timeframe ?? "7d";
      const page = options?.page ?? 1;
      const pageSize = options?.pageSize ?? 50;
      const depth = options?.depth ?? 1;
      const response = await this.client.get(`/${project}/memory/recent`, {
        params: { timeframe, depth, page, page_size: pageSize },
      });
      return { success: true, data: response.data };
    } catch (error: any) {
      const detail = error?.response?.data?.detail ?? error?.message ?? "Failed to load recent activity";
      return { success: false, error: String(detail) };
    }
  }

  async createProject(
    name: string,
    path: string,
    description = "",
    setDefault = false,
  ): Promise<ApiResponse> {
    try {
      const response = await this.client.post("/projects", {
        name,
        path,
        description,
        set_default: setDefault,
      });
      return { success: response.data.status === "success", data: response.data };
    } catch (error) {
      return { success: false, error: "Failed to create project" };
    }
  }

  async switchProject(name: string): Promise<ApiResponse> {
    try {
      const response = await this.client.put(`/projects/${name}/default`);
      if (response.data.status === "success") {
        this.activeProject = name;
      }
      return { success: response.data.status === "success", data: response.data };
    } catch (error) {
      return { success: false, error: "Failed to switch project" };
    }
  }

  async deleteProject(name: string): Promise<ApiResponse> {
    try {
      const response = await this.client.delete(`/projects/${name}`);
      return { success: response.data.status === "success", data: response.data };
    } catch (error) {
      return { success: false, error: "Failed to delete project" };
    }
  }

  /** Full project_info payload (stats, activity, system) for the active URL project segment. */
  async getProjectStats(): Promise<ApiResponse<Record<string, unknown>>> {
    try {
      const p = encodeURIComponent(this.activeProject);
      const response = await this.client.get(`/${p}/project/info`);
      return { success: true, data: response.data as Record<string, unknown> };
    } catch (error) {
      return { success: false, error: "Failed to load vault stats" };
    }
  }

  /** Scan markdown on disk into the DB (CLI-style sync). Uses project name (matches default/switch). */
  async syncVaultFiles(projectName?: string): Promise<ApiResponse<Record<string, unknown>>> {
    const name = projectName || this.activeProject;
    try {
      const response = await this.client.post(
        `/projects/${encodeURIComponent(name)}/sync`,
        {},
        { timeout: VAULT_LONG_OPERATION_TIMEOUT_MS },
      );
      return { success: true, data: response.data as Record<string, unknown> };
    } catch (error: any) {
      const detail = error?.response?.data?.detail ?? error?.message ?? "Vault sync failed";
      return { success: false, error: String(detail) };
    }
  }

  /** Align DB project rows with the config file (does not scan note files). */
  async syncProjectsRegistry(): Promise<ApiResponse> {
    try {
      const response = await this.client.post("/projects/sync");
      return { success: response.data?.status === "success", data: response.data };
    } catch (error: any) {
      const detail = error?.response?.data?.detail ?? error?.message ?? "Registry sync failed";
      return { success: false, error: String(detail) };
    }
  }

  /** Rebuild FTS / search index for the project (can take several minutes). */
  async reindexSearch(project?: string): Promise<ApiResponse> {
    try {
      const p = encodeURIComponent(project || this.activeProject);
      const response = await this.client.post(
        `/${p}/search/reindex`,
        {},
        { timeout: VAULT_LONG_OPERATION_TIMEOUT_MS },
      );
      return { success: true, data: response.data };
    } catch (error: any) {
      const detail = error?.response?.data?.detail ?? error?.message ?? "Reindex failed";
      return { success: false, error: String(detail) };
    }
  }

  /** Extra LanceDB roots (absolute paths on the API host). Persisted in config.json. */
  async getRagExtraRoots(): Promise<ApiResponse<{ paths: string[] }>> {
    try {
      const response = await this.client.get("/management/rag-extra-roots");
      const body = response.data as { success?: boolean; data?: { paths: string[] } };
      if (body?.data?.paths !== undefined) {
        return { success: true, data: { paths: body.data.paths } };
      }
      return { success: false, error: "Unexpected response from rag-extra-roots" };
    } catch (error: any) {
      const detail = error?.response?.data?.detail ?? error?.message ?? "Failed to load RAG extra roots";
      return { success: false, error: String(detail) };
    }
  }

  async setRagExtraRoots(paths: string[]): Promise<ApiResponse<{ paths: string[] }>> {
    try {
      const response = await this.client.put("/management/rag-extra-roots", { paths });
      const body = response.data as { success?: boolean; data?: { paths: string[] } };
      if (body?.data?.paths !== undefined) {
        return { success: true, data: { paths: body.data.paths } };
      }
      return { success: false, error: "Unexpected response from rag-extra-roots" };
    } catch (error: any) {
      const detail = error?.response?.data?.detail ?? error?.message ?? "Failed to save RAG extra roots";
      return { success: false, error: String(detail) };
    }
  }

  async validateRagExtraRoots(paths: string[]): Promise<
    ApiResponse<{
      items: Array<{ path: string; ok: boolean; resolved: string; error?: string }>;
    }>
  > {
    try {
      const response = await this.client.post("/management/rag-extra-roots/validate", { paths });
      const body = response.data as {
        success?: boolean;
        data?: { items: Array<{ path: string; ok: boolean; resolved: string; error?: string }> };
      };
      if (body?.data?.items !== undefined) {
        return { success: true, data: { items: body.data.items } };
      }
      return { success: false, error: "Unexpected response from validate" };
    } catch (error: any) {
      const detail = error?.response?.data?.detail ?? error?.message ?? "Validate failed";
      return { success: false, error: String(detail) };
    }
  }

  async getWatchStatus(): Promise<ApiResponse<{ running: boolean }>> {
    try {
      const response = await this.client.get("/management/watch/status");
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: "Failed to read watch status" };
    }
  }

  /** Filesystem sync progress (populated while vault scan runs). */
  async getSyncOperationStatus(): Promise<
    ApiResponse<{
      global_status: string;
      is_syncing: boolean;
      projects: Array<{
        project_name: string;
        status: string;
        message: string;
        files_processed: number;
        files_total: number;
        percent: number | null;
        error: string | null;
      }>;
    }>
  > {
    try {
      const response = await this.client.get("/management/sync/status");
      return { success: true, data: response.data };
    } catch (error) {
      return { success: false, error: "Failed to read sync status" };
    }
  }

  async startWatch(): Promise<ApiResponse<{ running: boolean }>> {
    try {
      const response = await this.client.post("/management/watch/start");
      return { success: true, data: response.data };
    } catch (error: any) {
      const detail = error?.response?.data?.detail ?? error?.message ?? "Failed to start watch";
      return { success: false, error: String(detail) };
    }
  }

  async stopWatch(): Promise<ApiResponse<{ running: boolean }>> {
    try {
      const response = await this.client.post("/management/watch/stop");
      return { success: true, data: response.data };
    } catch (error: any) {
      const detail = error?.response?.data?.detail ?? error?.message ?? "Failed to stop watch";
      return { success: false, error: String(detail) };
    }
  }

  // Graph Data (PointCloud)
  async getGraphSubgraph(options?: {
    center?: string | null;
    depth?: number;
    max_nodes?: number;
    max_edges?: number;
    include_unresolved?: boolean;
    seed_size?: number;
  }): Promise<
    ApiResponse<{
      nodes: any[];
      links: any[];
      meta?: Record<string, unknown>;
    }>
  > {
    try {
      const project = encodeURIComponent(this.activeProject);
      const params = new URLSearchParams();
      const c = options?.center;
      if (c !== undefined && c !== null && String(c).trim() !== "") {
        params.set("center", String(c).trim());
      }
      if (options?.depth !== undefined) params.set("depth", String(options.depth));
      if (options?.max_nodes !== undefined) params.set("max_nodes", String(options.max_nodes));
      if (options?.max_edges !== undefined) params.set("max_edges", String(options.max_edges));
      if (options?.include_unresolved === false) params.set("include_unresolved", "false");
      if (options?.seed_size !== undefined) params.set("seed_size", String(options.seed_size));
      const qs = params.toString();
      const path = `/${project}/knowledge/graph/subgraph${qs ? `?${qs}` : ""}`;
      const response = await this.client.get(path);
      const body = response.data;
      if (body?.nodes && body?.links) {
        return {
          success: true,
          data: { nodes: body.nodes, links: body.links, meta: body.meta },
        };
      }
      return { success: false, error: "Graph response missing nodes/links" };
    } catch (error) {
      return { success: false, error: "Failed to fetch graph data" };
    }
  }

  // Batch Import
  async scanImportDir(path: string, months = 0): Promise<ApiResponse<any[]>> {
    try {
      const response = await this.client.post("/import/scan", { path, months });
      return response.data;
    } catch (error) {
      return { success: false, error: "Failed to scan directory" };
    }
  }

  async runBatchImport(
    files: string[],
    destinationFolder: string,
    project?: string,
  ): Promise<ApiResponse<any[]>> {
    try {
      const response = await this.client.post("/import/batch", {
        files,
        destination_folder: destinationFolder,
        project,
      });
      return response.data;
    } catch (error) {
      return { success: false, error: "Batch import failed" };
    }
  }

  // Hardware and Model Management
  async detectHardware(): Promise<ApiResponse> {
    try {
      const response = await this.client.get("/hardware/detect");
      return response.data;
    } catch (error) {
      return { success: false, error: "Failed to detect hardware" };
    }
  }

  async optimizeModelParams(params: Record<string, any>): Promise<ApiResponse> {
    try {
      const response = await this.client.post("/model/optimize", params);
      return response.data;
    } catch (error) {
      return { success: false, error: "Failed to optimize model parameters" };
    }
  }

  // Test runner (requires ENABLE_WEBAPP_TESTS=1 on backend)
  async runTests(options?: {
    target?: string;
    timeout_seconds?: number;
    extra_args?: string[];
  }): Promise<
    ApiResponse<{
      success: boolean;
      exit_code: number;
      stdout: string;
      stderr: string;
      duration_seconds: number;
    }>
  > {
    try {
      const body = {
        target: options?.target ?? "tests",
        timeout_seconds: options?.timeout_seconds ?? 300,
        extra_args: options?.extra_args ?? [],
      };
      const response = await this.client.post("/tests/run", body, {
        timeout: (body.timeout_seconds + 10) * 1000,
      });
      return response.data;
    } catch (error: any) {
      const status = error?.response?.status;
      const detail = error?.response?.data?.detail ?? error?.message ?? "Test run failed";
      if (status === 403) {
        return { success: false, error: detail };
      }
      return {
        success: false,
        error: detail,
        data: {
          success: false,
          exit_code: -1,
          stdout: "",
          stderr: String(detail),
          duration_seconds: 0,
        },
      };
    }
  }

  // Generic MCP tool caller (for skill creator, research, etc.)
  async callMCPTool(toolName: string, args: Record<string, any>): Promise<ApiResponse> {
    try {
      const response = await this.client.post(`/mcp/tools/${toolName}`, {
        arguments: args,
      });
      return response.data;
    } catch (error) {
      return { success: false, error: `Failed to call ${toolName}` };
    }
  }
}

// Export singleton instance
export const apiService = new ApiService();
export default apiService;
