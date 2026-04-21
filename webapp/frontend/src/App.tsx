import { useState } from "react";
import { Route, Routes } from "react-router-dom";
import Layout from "./components/layout/Layout";
import Apps from "./pages/apps/Apps";
import AppsHub from "./pages/apps/AppsHub";
import AudioHub from "./pages/audio/AudioHub";
import Chat from "./pages/chat/Chat";
import Checkpoints from "./pages/checkpoints/Checkpoints";
import ControlRoom from "./pages/dashboard/ControlRoom";
import Dashboard from "./pages/dashboard/Dashboard";
import GraphCanvas from "./pages/dashboard/GraphCanvas";
import KnowledgeGraph from "./pages/dashboard/KnowledgeGraph";
import NoteViewer from "./pages/dashboard/NoteViewer";
import Recents from "./pages/dashboard/Recents";
import Skills from "./pages/dashboard/Skills";
import Tools from "./pages/dashboard/Tools";
import ZettelFlow from "./pages/dashboard/ZettelFlow";
import Help from "./pages/help/Help";
import BatchImport from "./pages/import-export/BatchImport";
import ImportExport from "./pages/import-export/ImportExport";
import Projects from "./pages/projects/Projects";
import ResearchLab from "./pages/research/ResearchLab";
import SearchDeep from "./pages/search/SearchDeep";
import Settings from "./pages/settings/Settings";
import SkillCreator from "./pages/skills/SkillCreator";
import SkillMarketplace from "./pages/skills/SkillMarketplace";
import SkillResearch from "./pages/skills/SkillResearch";
import SkillStudio from "./pages/skills/SkillStudio";
import LoggerPage from "./pages/system/LoggerPage";
import VaultStats from "./pages/system/VaultStats";
import VaultSync from "./pages/system/VaultSync";
import Tests from "./pages/tests/Tests";
import ZettelMaster from "./pages/zettelkasten/ZettelMaster";
import { apiService } from "./services/api";

/** ``GET .../content`` returns ``NoteContentResponse`` (title, permalink, content) — not full ``NoteResult``. */
function metadataTagsFromApi(raw: unknown): string[] {
  if (Array.isArray(raw)) {
    return raw.map((t) => String(t)).filter((t) => t.length > 0);
  }
  return [];
}

function App() {
  const [selectedNoteId, setSelectedNoteId] = useState<string | undefined>();
  const [selectedNoteMetadata, setSelectedNoteMetadata] = useState<any>(null);

  const handleNoteSelect = async (noteId: string) => {
    if (!noteId) {
      setSelectedNoteId(undefined);
      setSelectedNoteMetadata(null);
      return;
    }
    setSelectedNoteId(noteId);

    try {
      // Try to fetch real note metadata from API
      const response = await apiService.getNote(noteId);
      if (response.success && response.data) {
        const d = response.data as {
          title?: string;
          permalink?: string;
          content?: string;
          tags?: unknown;
          created?: string;
          modified?: string;
          wordCount?: number;
          connections?: number;
          backlinks?: number;
          readingTime?: number;
          fileSize?: string;
          id?: string;
        };
        const contentStr = typeof d.content === "string" ? d.content : "";
        const wordCount =
          typeof d.wordCount === "number" ? d.wordCount : Math.max(0, Math.round(contentStr.length / 5));
        const readingTime =
          typeof d.readingTime === "number"
            ? d.readingTime
            : Math.max(1, Math.ceil(wordCount / 200) || 1);
        setSelectedNoteMetadata({
          id: d.id ?? noteId,
          title: d.title ?? "Untitled",
          tags: metadataTagsFromApi(d.tags),
          created: d.created ?? new Date().toISOString(),
          modified: d.modified ?? new Date().toISOString(),
          wordCount,
          connections: typeof d.connections === "number" ? d.connections : 0,
          backlinks: typeof d.backlinks === "number" ? d.backlinks : 0,
          readingTime,
          fileSize: d.fileSize ?? `${(contentStr.length * 0.001).toFixed(1)} KB`,
        });
        return;
      }
    } catch (error) {
      console.error("Failed to fetch note metadata:", error);
      setSelectedNoteMetadata(null);
    }
  };

  const handleMetadataExport = async (format: string) => {
    if (!selectedNoteId) return;

    try {
      const response = await apiService.exportNote(selectedNoteId, format);
      if (response.success && response.data?.url) {
        // Trigger download
        const link = document.createElement("a");
        link.href = response.data.url;
        link.download = `note-${selectedNoteId}.${format}`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      } else {
        throw new Error("Export failed");
      }
    } catch (error) {
      console.error("Export failed:", error);
      throw error;
    }
  };

  const handleMetadataEdit = () => {
    // editing note - handler invoked
    // TODO: Implement edit functionality
  };

  const handleMetadataDelete = () => {
    // deleting note - handler invoked
    // TODO: Implement delete functionality
  };

  return (
    <Routes>
      <Route
        path="/"
        element={
          <Layout>
            <Dashboard />
          </Layout>
        }
      />

      <Route
        path="/notes"
        element={
          <Layout
            showMetadataSidebar={true}
            selectedNoteMetadata={selectedNoteMetadata}
            onMetadataExport={handleMetadataExport}
            onMetadataEdit={handleMetadataEdit}
            onMetadataDelete={handleMetadataDelete}
          >
            <NoteViewer selectedNoteId={selectedNoteId} onNoteSelect={handleNoteSelect} />
          </Layout>
        }
      />

      <Route
        path="/skills"
        element={
          <Layout>
            <Skills />
          </Layout>
        }
      />

      <Route
        path="/knowledge-graph"
        element={
          <Layout>
            <KnowledgeGraph />
          </Layout>
        }
      />

      <Route
        path="/import-export"
        element={
          <Layout>
            <ImportExport />
          </Layout>
        }
      />

      <Route
        path="/batch-import"
        element={
          <Layout>
            <BatchImport />
          </Layout>
        }
      />

      <Route
        path="/projects"
        element={
          <Layout>
            <Projects />
          </Layout>
        }
      />

      <Route
        path="/recents"
        element={
          <Layout>
            <Recents />
          </Layout>
        }
      />

      <Route
        path="/chat"
        element={
          <Layout>
            <Chat />
          </Layout>
        }
      />

      <Route
        path="/apps"
        element={
          <Layout>
            <Apps />
          </Layout>
        }
      />

      <Route
        path="/skills/create"
        element={
          <Layout>
            <SkillCreator />
          </Layout>
        }
      />

      <Route
        path="/skills/research"
        element={
          <Layout>
            <SkillResearch />
          </Layout>
        }
      />

      <Route
        path="/marketplace"
        element={
          <Layout>
            <SkillMarketplace />
          </Layout>
        }
      />

      <Route
        path="/research"
        element={
          <Layout>
            <ResearchLab />
          </Layout>
        }
      />

      <Route
        path="/zettelflow"
        element={
          <Layout>
            <ZettelFlow />
          </Layout>
        }
      />

      <Route
        path="/research/deep"
        element={
          <Layout>
            <SearchDeep />
          </Layout>
        }
      />

      <Route
        path="/skills/studio"
        element={
          <Layout>
            <SkillStudio />
          </Layout>
        }
      />

      <Route
        path="/apps-hub"
        element={
          <Layout>
            <AppsHub />
          </Layout>
        }
      />

      <Route
        path="/control-room"
        element={
          <Layout>
            <ControlRoom />
          </Layout>
        }
      />

      <Route
        path="/dashboard/zettelkasten"
        element={
          <Layout>
            <ZettelMaster />
          </Layout>
        }
      />

      <Route
        path="/dashboard/canvas"
        element={
          <Layout>
            <GraphCanvas />
          </Layout>
        }
      />

      <Route
        path="/audio"
        element={
          <Layout>
            <AudioHub />
          </Layout>
        }
      />

      <Route
        path="/checkpoints"
        element={
          <Layout>
            <Checkpoints />
          </Layout>
        }
      />

      <Route
        path="/settings"
        element={
          <Layout>
            <Settings />
          </Layout>
        }
      />

      <Route
        path="/help"
        element={
          <Layout>
            <Help />
          </Layout>
        }
      />

      <Route
        path="/logs"
        element={
          <Layout>
            <LoggerPage />
          </Layout>
        }
      />

      <Route
        path="/vault/sync"
        element={
          <Layout>
            <VaultSync />
          </Layout>
        }
      />

      <Route
        path="/vault/stats"
        element={
          <Layout>
            <VaultStats />
          </Layout>
        }
      />

      <Route
        path="/tools"
        element={
          <Layout>
            <Tools />
          </Layout>
        }
      />

      <Route
        path="/tests"
        element={
          <Layout>
            <Tests />
          </Layout>
        }
      />
    </Routes>
  );
}

export default App;
