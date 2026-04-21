import { HelpCircle, Menu, Terminal, Wifi, WifiOff } from "lucide-react";
import { Link } from "react-router-dom";

interface TopbarProps {
  onMenuClick: () => void;
  sidebarCollapsed: boolean;
}

export default function Topbar({ onMenuClick, sidebarCollapsed }: TopbarProps) {
  // Mock connection status - would be connected to actual service
  const isConnected = true;

  return (
    <header className="sticky top-0 z-30 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b border-border">
      <div className="flex h-16 items-center justify-between px-4 lg:px-8">
        {/* Left side - Menu button and connection status */}
        <div className="flex items-center">
          <button
            onClick={onMenuClick}
            className="p-2 rounded-md hover:bg-muted transition-colors"
            title={sidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            <Menu className="h-5 w-5" />
          </button>

          {/* Connection status */}
          <div className="flex items-center ml-4">
            {isConnected ? (
              <Wifi className="h-4 w-4 text-green-500" />
            ) : (
              <WifiOff className="h-4 w-4 text-red-500" />
            )}
            <span className="ml-2 text-sm text-muted-foreground">
              {isConnected ? "Connected" : "Disconnected"}
            </span>
          </div>
        </div>

        {/* Center - Title */}
        <div className="hidden md:block">
          <h1 className="text-lg font-semibold">Dashboard</h1>
        </div>

        {/* Right side - Action buttons */}
        <div className="flex items-center space-x-2">
          <Link
            to="/logs"
            className="p-2 rounded-md hover:bg-muted transition-colors"
            title="System log"
          >
            <Terminal className="h-5 w-5" />
          </Link>

          <Link to="/help" className="p-2 rounded-md hover:bg-muted transition-colors" title="Help">
            <HelpCircle className="h-5 w-5" />
          </Link>
        </div>
      </div>
    </header>
  );
}
