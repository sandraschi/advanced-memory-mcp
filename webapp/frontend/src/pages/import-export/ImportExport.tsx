import { AlertCircle, ArrowLeftRight, CheckCircle, Download, Loader2, Upload } from "lucide-react";
import { useState } from "react";
import { apiService } from "../../services/api";

type Tab = "import" | "export";

export default function ImportExport() {
  const [activeTab, setActiveTab] = useState<Tab>("import");
  const [format, setFormat] = useState("");
  const [path, setPath] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<{ success: boolean; message: string } | null>(null);

  const handleImport = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!format || !path) return;

    setIsLoading(true);
    setResult(null);
    try {
      const response = await apiService.importData(format, path);
      setResult({
        success: response.success,
        message: response.success
          ? "Import completed successfully"
          : response.error || "Import failed",
      });
    } catch (error) {
      setResult({ success: false, message: "An unexpected error occurred during import" });
    } finally {
      setIsLoading(false);
    }
  };

  const handleExport = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!format || !path) return;

    setIsLoading(true);
    setResult(null);
    try {
      const response = await apiService.exportData(format, path);
      setResult({
        success: response.success,
        message: response.success
          ? "Export completed successfully"
          : response.error || "Export failed",
      });
    } catch (error) {
      setResult({ success: false, message: "An unexpected error occurred during export" });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="flex items-center space-x-3 mb-2">
        <ArrowLeftRight className="h-8 w-8 text-accent" />
        <h1 className="text-3xl font-bold tracking-tight">Import / Export</h1>
      </div>

      <div className="card">
        <div className="flex border-b border-white/10">
          <button
            onClick={() => {
              setActiveTab("import");
              setResult(null);
              setFormat("");
              setPath("");
            }}
            className={`px-6 py-4 font-medium transition-colors relative ${
              activeTab === "import" ? "text-accent" : "text-muted-foreground hover:text-foreground"
            }`}
          >
            Import Data
            {activeTab === "import" && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-accent" />
            )}
          </button>
          <button
            onClick={() => {
              setActiveTab("export");
              setResult(null);
              setFormat("");
              setPath("");
            }}
            className={`px-6 py-4 font-medium transition-colors relative ${
              activeTab === "export" ? "text-accent" : "text-muted-foreground hover:text-foreground"
            }`}
          >
            Export Data
            {activeTab === "export" && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-accent" />
            )}
          </button>
        </div>

        <div className="p-8">
          {activeTab === "import" ? (
            <form onSubmit={handleImport} className="space-y-6">
              <div className="space-y-2">
                <label className="text-sm font-medium">Source Format</label>
                <select
                  value={format}
                  onChange={(e) => setFormat(e.target.value)}
                  className="w-full bg-background border border-white/10 rounded-md px-4 py-2 focus:outline-none focus:ring-2 focus:ring-accent/50"
                  required
                >
                  <option value="">Select format...</option>
                  <option value="obsidian">Obsidian Vault</option>
                  <option value="notion">Notion Export (HTML)</option>
                  <option value="joplin">Joplin Export</option>
                  <option value="evernote">Evernote (.enex)</option>
                  <option value="onenote">OneNote HTML</option>
                </select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Source Path</label>
                <input
                  type="text"
                  value={path}
                  onChange={(e) => setPath(e.target.value)}
                  placeholder="e.g. C:\Users\Sandra\Documents\MyNotes"
                  className="w-full bg-background border border-white/10 rounded-md px-4 py-2 focus:outline-none focus:ring-2 focus:ring-accent/50"
                  required
                />
              </div>

              <button
                type="submit"
                disabled={isLoading || !format || !path}
                className="btn btn-primary w-full flex items-center justify-center space-x-2 py-3"
              >
                {isLoading ? (
                  <Loader2 className="h-5 w-5 animate-spin" />
                ) : (
                  <Upload className="h-5 w-5" />
                )}
                <span>{isLoading ? "Importing..." : "Start Import"}</span>
              </button>
            </form>
          ) : (
            <form onSubmit={handleExport} className="space-y-6">
              <div className="space-y-2">
                <label className="text-sm font-medium">Export Format</label>
                <select
                  value={format}
                  onChange={(e) => setFormat(e.target.value)}
                  className="w-full bg-background border border-white/10 rounded-md px-4 py-2 focus:outline-none focus:ring-2 focus:ring-accent/50"
                  required
                >
                  <option value="">Select format...</option>
                  <option value="html">Static HTML Website</option>
                  <option value="pdf">Combined PDF Book</option>
                  <option value="pandoc">Pandoc Markdown</option>
                  <option value="docsify">Docsify Knowledge Base</option>
                  <option value="archive">Full ZIP Archive</option>
                </select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Destination Path</label>
                <input
                  type="text"
                  value={path}
                  onChange={(e) => setPath(e.target.value)}
                  placeholder="e.g. D:\Backups\Knowledge"
                  className="w-full bg-background border border-white/10 rounded-md px-4 py-2 focus:outline-none focus:ring-2 focus:ring-accent/50"
                  required
                />
              </div>

              <button
                type="submit"
                disabled={isLoading || !format || !path}
                className="btn btn-primary w-full flex items-center justify-center space-x-2 py-3"
              >
                {isLoading ? (
                  <Loader2 className="h-5 w-5 animate-spin" />
                ) : (
                  <Download className="h-5 w-5" />
                )}
                <span>{isLoading ? "Exporting..." : "Start Export"}</span>
              </button>
            </form>
          )}

          {result && (
            <div
              className={`mt-8 p-4 rounded-md flex items-start space-x-3 ${
                result.success
                  ? "bg-green-500/10 border border-green-500/20 text-green-400"
                  : "bg-red-500/10 border border-red-500/20 text-red-400"
              }`}
            >
              {result.success ? (
                <CheckCircle className="h-5 w-5 mt-0.5" />
              ) : (
                <AlertCircle className="h-5 w-5 mt-0.5" />
              )}
              <div>
                <div className="font-semibold">{result.success ? "Success" : "Error"}</div>
                <div className="text-sm opacity-90">{result.message}</div>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <div className="card p-6 border-l-4 border-accent">
          <h3 className="font-bold mb-2 flex items-center">
            <Upload className="h-4 w-4 mr-2" />
            Import Logic
          </h3>
          <p className="text-sm text-muted-foreground">
            Imports are processed atomically. Each note becomes an Entity, and YAML frontmatter is
            converted to Observations and Tags. Existing notes with identical permalinks will be
            matched and updated if necessary.
          </p>
        </div>
        <div className="card p-6 border-l-4 border-accent">
          <h3 className="font-bold mb-2 flex items-center">
            <Download className="h-4 w-4 mr-2" />
            Export Specs
          </h3>
          <p className="text-sm text-muted-foreground">
            Exports resolve all `[[Relation]]` links and embed linked images. The HTML and Docsify
            formats include a searchable index based on the Graph content.
          </p>
        </div>
      </div>
    </div>
  );
}
