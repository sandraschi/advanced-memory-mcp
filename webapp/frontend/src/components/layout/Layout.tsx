import { useState } from "react";
import MetadataSidebar from "./MetadataSidebar";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";

interface LayoutProps {
  children: React.ReactNode;
  showMetadataSidebar?: boolean;
  selectedNoteMetadata?: any;
  onMetadataExport?: (format: string, noteId: string) => Promise<void>;
  onMetadataEdit?: () => void;
  onMetadataDelete?: () => void;
}

export default function Layout({
  children,
  showMetadataSidebar = false,
  selectedNoteMetadata,
  onMetadataExport,
  onMetadataEdit,
  onMetadataDelete,
}: LayoutProps) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [metadataSidebarOpen, setMetadataSidebarOpen] = useState(false);

  return (
    <div className="h-screen min-h-0 bg-[#020205] text-slate-50 font-inter selection:bg-indigo-500/30 flex overflow-hidden">
      {/* Left Sidebar */}
      <Sidebar
        isCollapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
      />

      {/* Main Content Area - min-h-0 so flex child can shrink and fill viewport */}
      <div className="flex min-h-0 min-w-0 flex-1 flex-col">
        {/* Topbar */}
        <Topbar
          onMenuClick={() => setSidebarCollapsed(!sidebarCollapsed)}
          sidebarCollapsed={sidebarCollapsed}
        />

        {/* Scrollable page shell — overflow was hidden here so nothing could scroll */}
        <main className="flex min-h-0 min-w-0 flex-1 flex-col overflow-hidden">
          <div className="app-scroll flex min-h-0 min-w-0 flex-1 flex-col overflow-y-auto overflow-x-hidden">
            {children}
          </div>
        </main>
      </div>

      {/* Right Metadata Sidebar */}
      {showMetadataSidebar && (
        <MetadataSidebar
          isOpen={metadataSidebarOpen}
          onToggle={() => setMetadataSidebarOpen(!metadataSidebarOpen)}
          note={selectedNoteMetadata}
          onExport={onMetadataExport}
          onEdit={onMetadataEdit}
          onDelete={onMetadataDelete}
        />
      )}
    </div>
  );
}
