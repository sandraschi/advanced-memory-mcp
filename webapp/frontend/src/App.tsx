import { useState } from 'react'
import { apiService } from './services/api'
import { Routes, Route } from 'react-router-dom'
import Layout from './components/layout/Layout'
import Dashboard from './pages/dashboard/Dashboard'
import NoteViewer from './pages/dashboard/NoteViewer'
import Skills from './pages/dashboard/Skills'
import KnowledgeGraph from './pages/dashboard/KnowledgeGraph'
import Settings from './pages/settings/Settings'
import Help from './pages/help/Help'
import ImportExport from './pages/import-export/ImportExport'
import BatchImport from './pages/import-export/BatchImport'
import Chat from './pages/chat/Chat'
import Apps from './pages/apps/Apps'
import SkillCreator from './pages/skills/SkillCreator'
import SkillResearch from './pages/skills/SkillResearch'
import SkillMarketplace from './pages/skills/SkillMarketplace'
import ResearchLab from './pages/research/ResearchLab'
import ZettelFlow from './pages/dashboard/ZettelFlow'
import SearchDeep from './pages/search/SearchDeep'
import GraphCanvas from './pages/dashboard/GraphCanvas'
import SkillStudio from './pages/skills/SkillStudio'
import AppsHub from './pages/apps/AppsHub'
import ControlRoom from './pages/dashboard/ControlRoom'
import Projects from './pages/projects/Projects'
import Recents from './pages/dashboard/Recents'
import ZettelMaster from './pages/zettelkasten/ZettelMaster'
import AudioHub from './pages/audio/AudioHub'
import Checkpoints from './pages/checkpoints/Checkpoints'
import Tools from './pages/dashboard/Tools'
import Tests from './pages/tests/Tests'

function App() {
  const [selectedNoteId, setSelectedNoteId] = useState<string | undefined>()
  const [selectedNoteMetadata, setSelectedNoteMetadata] = useState<any>(null)

  const handleNoteSelect = async (noteId: string) => {
    setSelectedNoteId(noteId)

    try {
      // Try to fetch real note metadata from API
      const response = await apiService.getNote(noteId)
      if (response.success && response.data) {
        setSelectedNoteMetadata({
          id: response.data.id,
          title: response.data.title,
          tags: response.data.tags,
          created: response.data.created,
          modified: response.data.modified,
          wordCount: response.data.wordCount,
          connections: response.data.connections,
          backlinks: response.data.backlinks || 0,
          readingTime: response.data.readingTime || Math.ceil(response.data.wordCount / 200),
          fileSize: response.data.fileSize || `${(response.data.content.length * 0.001).toFixed(1)} KB`
        })
        return
      }
    } catch (error) {
      console.error('Failed to fetch note metadata:', error)
      setSelectedNoteMetadata(null)
    }
  }

  const handleMetadataExport = async (format: string) => {
    if (!selectedNoteId) return

    try {
      const response = await apiService.exportNote(selectedNoteId, format)
      if (response.success && response.data?.url) {
        // Trigger download
        const link = document.createElement('a')
        link.href = response.data.url
        link.download = `note-${selectedNoteId}.${format}`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      } else {
        throw new Error('Export failed')
      }
    } catch (error) {
      console.error('Export failed:', error)
      throw error
    }
  }

  const handleMetadataEdit = () => {
    console.log('Editing note')
    // TODO: Implement edit functionality
  }

  const handleMetadataDelete = () => {
    console.log('Deleting note')
    // TODO: Implement delete functionality
  }

  return (
    <Routes>
      <Route path="/" element={
        <Layout>
          <Dashboard />
        </Layout>
      } />

      <Route path="/notes" element={
        <Layout
          showMetadataSidebar={true}
          selectedNoteMetadata={selectedNoteMetadata}
          onMetadataExport={handleMetadataExport}
          onMetadataEdit={handleMetadataEdit}
          onMetadataDelete={handleMetadataDelete}
        >
          <NoteViewer
            selectedNoteId={selectedNoteId}
            onNoteSelect={handleNoteSelect}
          />
        </Layout>
      } />

      <Route path="/skills" element={
        <Layout>
          <Skills />
        </Layout>
      } />

      <Route path="/knowledge-graph" element={
        <Layout>
          <KnowledgeGraph />
        </Layout>
      } />

      <Route path="/import-export" element={
        <Layout>
          <ImportExport />
        </Layout>
      } />

      <Route path="/batch-import" element={
        <Layout>
          <BatchImport />
        </Layout>
      } />

      <Route path="/projects" element={
        <Layout>
          <Projects />
        </Layout>
      } />

      <Route path="/recents" element={
        <Layout>
          <Recents />
        </Layout>
      } />

      <Route path="/chat" element={
        <Layout>
          <Chat />
        </Layout>
      } />

      <Route path="/apps" element={
        <Layout>
          <Apps />
        </Layout>
      } />

      <Route path="/skills/create" element={
        <Layout>
          <SkillCreator />
        </Layout>
      } />

      <Route path="/skills/research" element={
        <Layout>
          <SkillResearch />
        </Layout>
      } />

      <Route path="/marketplace" element={
        <Layout>
          <SkillMarketplace />
        </Layout>
      } />

      <Route path="/research" element={
        <Layout>
          <ResearchLab />
        </Layout>
      } />

      <Route path="/zettelflow" element={
        <Layout>
          <ZettelFlow />
        </Layout>
      } />

      <Route path="/research/deep" element={
        <Layout>
          <SearchDeep />
        </Layout>
      } />

      <Route path="/skills/studio" element={
        <Layout>
          <SkillStudio />
        </Layout>
      } />

      <Route path="/apps-hub" element={
        <Layout>
          <AppsHub />
        </Layout>
      } />

      <Route path="/control-room" element={
        <Layout>
          <ControlRoom />
        </Layout>
      } />

      <Route path="/dashboard/zettelkasten" element={
        <Layout>
          <ZettelMaster />
        </Layout>
      } />

      <Route path="/dashboard/canvas" element={
        <Layout>
          <GraphCanvas />
        </Layout>
      } />

      <Route path="/audio" element={
        <Layout>
          <AudioHub />
        </Layout>
      } />

      <Route path="/checkpoints" element={
        <Layout>
          <Checkpoints />
        </Layout>
      } />

      <Route path="/settings" element={
        <Layout>
          <Settings />
        </Layout>
      } />

      <Route path="/help" element={
        <Layout>
          <Help />
        </Layout>
      } />

      <Route path="/tools" element={
        <Layout>
          <Tools />
        </Layout>
      } />

      <Route path="/tests" element={
        <Layout>
          <Tests />
        </Layout>
      } />
    </Routes>
  )
}

export default App
