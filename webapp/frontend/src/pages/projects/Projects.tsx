import {
  Briefcase,
  CheckCircle2,
  ChevronRight,
  ExternalLink,
  FolderPlus,
  Loader2,
  ShieldAlert,
  Trash2,
} from "lucide-react";
import { useEffect, useState } from "react";
import { apiService } from "../../services/api";

interface Project {
  name: string;
  path: string;
  description?: string;
  is_default?: boolean;
  status?: string;
}

export default function Projects() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Create project form
  const [showCreate, setShowCreate] = useState(false);
  const [newName, setNewName] = useState("");
  const [newPath, setNewPath] = useState("");
  const [newDesc, setNewDesc] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Delete confirmation
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);
  const [deleteConfirmedOnce, setDeleteConfirmedOnce] = useState(false);

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    setIsLoading(true);
    try {
      const response = await apiService.getProjects();
      if (response.success && response.data) {
        setProjects(response.data);
      } else {
        setError(response.error || "Failed to load projects");
      }
    } catch (err) {
      setError("An unexpected error occurred");
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const response = await apiService.createProject(newName, newPath, newDesc);
      if (response.success) {
        setNewName("");
        setNewPath("");
        setNewDesc("");
        setShowCreate(false);
        fetchProjects();
      } else {
        alert(response.error || "Failed to create project");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSwitch = async (name: string) => {
    try {
      const response = await apiService.switchProject(name);
      if (response.success) {
        fetchProjects(); // Refresh to see new active project
      } else {
        alert(response.error || "Failed to switch project");
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async (name: string) => {
    if (!deleteConfirmedOnce) {
      setDeleteConfirmedOnce(true);
      return;
    }

    try {
      const response = await apiService.deleteProject(name);
      if (response.success) {
        setDeleteConfirm(null);
        setDeleteConfirmedOnce(false);
        fetchProjects();
      } else {
        alert(response.error || "Failed to delete project");
      }
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-accent/20 rounded-lg">
            <Briefcase className="h-8 w-8 text-accent" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Project Management</h1>
            <p className="text-muted-foreground text-sm">
              Organize your knowledge bases and workspaces
            </p>
          </div>
        </div>

        <button
          onClick={() => setShowCreate(!showCreate)}
          className={`btn ${showCreate ? "btn-outline" : "btn-primary"} flex items-center space-x-2`}
        >
          <FolderPlus className="h-4 w-4" />
          <span>{showCreate ? "Cancel" : "New Project"}</span>
        </button>
      </div>

      {showCreate && (
        <div className="card p-6 border-accent/30 bg-accent/5 animate-in zoom-in-95 duration-200">
          <h2 className="text-xl font-semibold mb-4">Create New Project</h2>
          <form onSubmit={handleCreate} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Project Name</label>
              <input
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                placeholder="e.g. Robotics Research"
                className="w-full bg-background border border-border rounded-md px-4 py-2 focus:ring-2 focus:ring-accent/50 outline-none"
                required
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Filesystem Path</label>
              <input
                value={newPath}
                onChange={(e) => setNewPath(e.target.value)}
                placeholder="e.g. D:\Notes\Robotics"
                className="w-full bg-background border border-border rounded-md px-4 py-2 focus:ring-2 focus:ring-accent/50 outline-none"
                required
              />
            </div>
            <div className="md:col-span-2 space-y-2">
              <label className="text-sm font-medium">Description (Optional)</label>
              <textarea
                value={newDesc}
                onChange={(e) => setNewDesc(e.target.value)}
                placeholder="Briefly describe this project's scope..."
                className="w-full bg-background border border-border rounded-md px-4 py-2 focus:ring-2 focus:ring-accent/50 outline-none h-20"
              />
            </div>
            <div className="md:col-span-2 flex justify-end">
              <button
                type="submit"
                disabled={isSubmitting}
                className="btn btn-primary flex items-center space-x-2 px-8"
              >
                {isSubmitting ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <CheckCircle2 className="h-4 w-4" />
                )}
                <span>Create Project</span>
              </button>
            </div>
          </form>
        </div>
      )}

      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-20 space-y-4">
          <Loader2 className="h-12 w-12 text-accent animate-spin" />
          <p className="text-muted-foreground animate-pulse">Scanning workspaces...</p>
        </div>
      ) : error ? (
        <div className="card p-8 text-center border-red-500/30 bg-red-500/5">
          <ShieldAlert className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-xl font-bold text-red-400">Error Loading Projects</h3>
          <p className="text-muted-foreground mt-2">{error}</p>
          <button onClick={fetchProjects} className="btn btn-outline btn-sm mt-6">
            Try Again
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project) => (
            <div
              key={project.name}
              className={`card group hover:scale-[1.02] transition-all duration-300 overflow-hidden border-border/50 ${project.is_default ? "ring-2 ring-accent border-transparent" : ""}`}
            >
              <div className="p-6">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <h3 className="font-bold text-xl truncate max-w-[150px]">{project.name}</h3>
                    {project.is_default && (
                      <span className="px-2 py-0.5 bg-accent/20 text-accent text-[10px] font-bold rounded uppercase tracking-wider">
                        Active
                      </span>
                    )}
                  </div>
                  <div className="flex space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    {!project.is_default && (
                      <button
                        onClick={() => setDeleteConfirm(project.name)}
                        className="p-1.5 text-muted-foreground hover:text-red-500 transition-colors"
                        title="Delete project"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    )}
                  </div>
                </div>

                <p className="text-sm text-muted-foreground line-clamp-2 mb-4 h-10">
                  {project.description || "No description provided."}
                </p>

                <div className="flex items-center text-xs text-muted-foreground mb-6 font-mono bg-background/50 p-2 rounded truncate border border-white/5">
                  <ChevronRight className="h-3 w-3 mr-1 text-accent" />
                  {project.path}
                </div>

                <div className="flex items-center justify-between mt-auto">
                  <button
                    onClick={() => handleSwitch(project.name)}
                    disabled={project.is_default}
                    className={`btn btn-sm ${project.is_default ? "btn-ghost cursor-default text-accent font-bold" : "btn-outline hover:bg-accent/10"} px-4`}
                  >
                    {project.is_default ? (
                      <CheckCircle2 className="h-4 w-4 mr-2" />
                    ) : (
                      <ExternalLink className="h-4 w-4 mr-2" />
                    )}
                    <span>{project.is_default ? "Connected" : "Connect"}</span>
                  </button>

                  <div className="text-[10px] text-muted-foreground font-medium uppercase tracking-widest opacity-50">
                    {project.status || "READY"}
                  </div>
                </div>
              </div>

              {/* Double Confirmation Overlay */}
              {deleteConfirm === project.name && (
                <div className="absolute inset-0 bg-background/95 backdrop-blur-sm flex flex-col items-center justify-center p-6 text-center animate-in fade-in duration-200">
                  <ShieldAlert className="h-10 w-10 text-red-500 mb-4" />
                  <h4 className="font-bold text-lg mb-1">Delete "{project.name}"?</h4>
                  <p className="text-xs text-muted-foreground mb-4">
                    {deleteConfirmedOnce
                      ? "FINAL WARNING: This action is permanent."
                      : "This will remove the project mapping, not your files."}
                  </p>
                  <div className="flex space-x-3 w-full">
                    <button
                      onClick={() => {
                        setDeleteConfirm(null);
                        setDeleteConfirmedOnce(false);
                      }}
                      className="flex-1 btn btn-ghost btn-sm"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={() => handleDelete(project.name)}
                      className="flex-1 btn btn-sm bg-red-600 hover:bg-red-700 text-white border-transparent"
                    >
                      {deleteConfirmedOnce ? "Confirm Delete" : "Delete"}
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}

          {/* Empty State / Quick Add */}
          {projects.length < 6 && projects.length > 0 && (
            <button
              onClick={() => setShowCreate(true)}
              className="card border-dashed border-2 border-border/50 hover:border-accent/40 hover:bg-accent/5 transition-all flex flex-col items-center justify-center p-8 space-y-3 min-h-[250px]"
            >
              <div className="p-3 bg-muted rounded-full">
                <FolderPlus className="h-8 w-8 text-muted-foreground" />
              </div>
              <div className="text-center">
                <p className="font-semibold text-muted-foreground">Add Another Project</p>
                <p className="text-xs text-muted-foreground/60">Expand your workspace</p>
              </div>
            </button>
          )}
        </div>
      )}
    </div>
  );
}
