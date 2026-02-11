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
    }

    // Fall back to mock metadata
    setSelectedNoteMetadata({
      id: noteId,
      title: `Note ${noteId}`,
      tags: ['sample', 'mock'],
      created: '2026-01-20 14:30:00',
      modified: '2026-01-20 15:45:00',
      wordCount: 1247,
      connections: 8,
      backlinks: 3,
      readingTime: 6,
      fileSize: '4.2 KB'
    })
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
    </Routes>
  )
}

export default App
