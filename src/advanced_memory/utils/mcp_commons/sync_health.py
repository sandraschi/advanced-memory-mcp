"""
Robust file sync health monitoring for MCP servers.

This module provides:
- Structured logging for sync operations
- Health checks and diagnostics
- Stall detection
- Automatic recovery
- Progress monitoring

Usage:
    sync_monitor = SyncHealthMonitor(project_path="/path/to/files")
    sync_monitor.start()
    
    # In your MCP tool:
    @mcp.tool()
    async def sync_health():
        return sync_monitor.get_health_report()
"""

import asyncio
import logging
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any

try:
    import structlog
    logger = structlog.get_logger(__name__)
    HAS_STRUCTLOG = True
except ImportError:
    logger = logging.getLogger(__name__)
    HAS_STRUCTLOG = False


class SyncState(Enum):
    """Sync states with clear semantics."""
    INITIALIZING = "initializing"
    COUNTING = "counting"
    SCANNING = "scanning"
    WATCHING = "watching"
    COMPLETED = "completed"
    ERROR_PERMISSION = "error_permission"
    ERROR_NOT_FOUND = "error_not_found"
    ERROR_TIMEOUT = "error_timeout"
    ERROR_UNKNOWN = "error_unknown"
    STALLED = "stalled"


@dataclass
class SyncMetrics:
    """Sync performance metrics."""
    files_total: int = 0
    files_scanned: int = 0
    files_per_second: float = 0.0
    bytes_processed: int = 0
    start_time: float = field(default_factory=time.time)
    last_progress_time: float = field(default_factory=time.time)
    errors_count: int = 0
    
    @property
    def runtime_seconds(self) -> float:
        """Get total runtime in seconds."""
        return time.time() - self.start_time
    
    @property
    def progress_percent(self) -> float:
        """Get progress percentage."""
        if self.files_total == 0:
            return 0.0
        return (self.files_scanned / self.files_total) * 100
    
    @property
    def time_since_progress(self) -> float:
        """Time since last progress update."""
        return time.time() - self.last_progress_time
    
    def update_progress(self, files_scanned: int):
        """Update progress metrics."""
        self.files_scanned = files_scanned
        self.last_progress_time = time.time()
        
        if self.runtime_seconds > 0:
            self.files_per_second = self.files_scanned / self.runtime_seconds


class SyncHealthMonitor:
    """
    Monitor file sync health and detect issues.
    
    Features:
    - Progress tracking
    - Stall detection
    - Error logging
    - Health diagnostics
    - Automatic recovery attempts
    """
    
    def __init__(
        self,
        project_path: str,
        stall_timeout: int = 60,
        check_interval: int = 10,
        max_recovery_attempts: int = 3,
    ):
        """
        Initialize sync health monitor.
        
        Args:
            project_path: Path to project directory
            stall_timeout: Seconds without progress before marking as stalled
            check_interval: Seconds between health checks
            max_recovery_attempts: Maximum automatic recovery attempts
        """
        self.project_path = Path(project_path)
        self.stall_timeout = stall_timeout
        self.check_interval = check_interval
        self.max_recovery_attempts = max_recovery_attempts
        
        self.state = SyncState.INITIALIZING
        self.metrics = SyncMetrics()
        self.errors: List[Dict[str, Any]] = []
        self.recovery_attempts = 0
        self.watcher = None
        
        self._monitor_task: Optional[asyncio.Task] = None
        self._is_monitoring = False
        
        self._log("sync_monitor_initialized",
                  project_path=str(self.project_path),
                  stall_timeout=stall_timeout)
    
    def _log(self, event: str, level: str = "info", **kwargs):
        """Log with structured or standard logging."""
        if HAS_STRUCTLOG:
            getattr(logger, level)(event, **kwargs)
        else:
            msg = f"{event}: {kwargs}"
            getattr(logger, level)(msg)
    
    def count_files(self) -> int:
        """Count markdown files in project."""
        try:
            self.state = SyncState.COUNTING
            self._log("counting_files", path=str(self.project_path))
            
            count = len(list(self.project_path.rglob("*.md")))
            
            self._log("file_count_complete", 
                     count=count,
                     path=str(self.project_path))
            
            return count
            
        except PermissionError as e:
            self.state = SyncState.ERROR_PERMISSION
            self._add_error("permission_denied", str(e))
            raise
            
        except FileNotFoundError as e:
            self.state = SyncState.ERROR_NOT_FOUND
            self._add_error("path_not_found", str(e))
            raise
            
        except Exception as e:
            self.state = SyncState.ERROR_UNKNOWN
            self._add_error("count_failed", str(e), traceback.format_exc())
            raise
    
    def start_scan(self) -> bool:
        """
        Start file scanning.
        
        Returns:
            True if started successfully, False otherwise
        """
        try:
            self._log("scan_starting")
            
            # Count files first
            self.metrics.files_total = self.count_files()
            
            if self.metrics.files_total == 0:
                self._log("no_files_found", level="warning")
                self.state = SyncState.COMPLETED
                return True
            
            self.state = SyncState.SCANNING
            self._log("scan_started",
                     total_files=self.metrics.files_total,
                     state=self.state.value)
            
            return True
            
        except Exception as e:
            self._log("scan_start_failed",
                     level="error",
                     error=str(e),
                     error_type=type(e).__name__)
            return False
    
    def update_scan_progress(self, files_scanned: int):
        """Update scan progress."""
        self.metrics.update_progress(files_scanned)
        
        if files_scanned == self.metrics.files_total:
            self.state = SyncState.COMPLETED
            self._log("scan_completed",
                     files=files_scanned,
                     duration=self.metrics.runtime_seconds)
        elif files_scanned % 100 == 0:
            # Log every 100 files
            self._log("scan_progress",
                     scanned=files_scanned,
                     total=self.metrics.files_total,
                     percent=self.metrics.progress_percent)
    
    def _add_error(self, error_type: str, message: str, trace: str = ""):
        """Add error to error log."""
        error = {
            "type": error_type,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "trace": trace,
        }
        self.errors.append(error)
        self.metrics.errors_count += 1
        
        self._log("error_logged",
                 level="error",
                 error_type=error_type,
                 message=message)
    
    async def start_monitoring(self):
        """Start background monitoring task."""
        if self._is_monitoring:
            self._log("monitoring_already_running", level="warning")
            return
        
        self._is_monitoring = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        self._log("monitoring_started")
    
    async def stop_monitoring(self):
        """Stop background monitoring."""
        self._is_monitoring = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        self._log("monitoring_stopped")
    
    async def _monitor_loop(self):
        """Background monitoring loop."""
        while self._is_monitoring:
            try:
                await asyncio.sleep(self.check_interval)
                await self._check_health()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self._log("monitor_error",
                         level="error",
                         error=str(e))
    
    async def _check_health(self):
        """Perform health check."""
        # Check for stall
        if self.state == SyncState.SCANNING:
            if self.metrics.time_since_progress > self.stall_timeout:
                self._log("sync_stalled",
                         level="warning",
                         time_since_progress=self.metrics.time_since_progress,
                         files_scanned=self.metrics.files_scanned)
                
                self.state = SyncState.STALLED
                await self._attempt_recovery()
        
        # Check watcher health
        if self.watcher and hasattr(self.watcher, 'is_alive'):
            if not self.watcher.is_alive():
                self._log("watcher_dead",
                         level="error")
                await self._attempt_recovery()
    
    async def _attempt_recovery(self):
        """Attempt to recover from errors."""
        if self.recovery_attempts >= self.max_recovery_attempts:
            self._log("max_recovery_attempts_reached",
                     level="error",
                     attempts=self.recovery_attempts)
            return
        
        self.recovery_attempts += 1
        self._log("attempting_recovery",
                 attempt=self.recovery_attempts,
                 max_attempts=self.max_recovery_attempts)
        
        try:
            # Reset state
            self.state = SyncState.INITIALIZING
            self.metrics = SyncMetrics()
            self.metrics.files_total = self.count_files()
            
            # Restart scan
            self.start_scan()
            
            self._log("recovery_successful",
                     attempt=self.recovery_attempts)
            
        except Exception as e:
            self._log("recovery_failed",
                     level="error",
                     attempt=self.recovery_attempts,
                     error=str(e))
    
    def get_health_report(self) -> Dict[str, Any]:
        """
        Get comprehensive health report.
        
        Returns:
            Dictionary with health status, metrics, and diagnostics
        """
        return {
            "healthy": self.state not in [
                SyncState.ERROR_PERMISSION,
                SyncState.ERROR_NOT_FOUND,
                SyncState.ERROR_TIMEOUT,
                SyncState.ERROR_UNKNOWN,
                SyncState.STALLED,
            ],
            "state": self.state.value,
            "metrics": {
                "files_total": self.metrics.files_total,
                "files_scanned": self.metrics.files_scanned,
                "progress_percent": round(self.metrics.progress_percent, 2),
                "files_per_second": round(self.metrics.files_per_second, 2),
                "runtime_seconds": round(self.metrics.runtime_seconds, 2),
                "time_since_progress": round(self.metrics.time_since_progress, 2),
                "errors_count": self.metrics.errors_count,
            },
            "watcher": {
                "exists": self.watcher is not None,
                "alive": self.watcher.is_alive() if self.watcher and hasattr(self.watcher, 'is_alive') else None,
            },
            "errors": self.errors[-10:],  # Last 10 errors
            "recovery_attempts": self.recovery_attempts,
            "recommendations": self._generate_recommendations(),
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations."""
        recs = []
        
        if self.state == SyncState.ERROR_PERMISSION:
            recs.append("⚠️  Permission error - check folder permissions")
        
        if self.state == SyncState.ERROR_NOT_FOUND:
            recs.append("❌ Path not found - verify project path exists")
        
        if self.state == SyncState.STALLED:
            recs.append("🐛 Sync appears stalled - automatic recovery attempted")
        
        if self.watcher and hasattr(self.watcher, 'is_alive') and not self.watcher.is_alive():
            recs.append("💀 Watcher is dead - restart server required")
        
        if self.metrics.files_per_second < 1 and self.metrics.files_scanned > 0:
            recs.append("🐌 Slow scan detected - check disk I/O or file count")
        
        if self.metrics.time_since_progress > 30 and self.state == SyncState.SCANNING:
            recs.append("⏱️  No progress for 30+ seconds - possible hang")
        
        if not recs:
            recs.append("✅ All systems healthy")
        
        return recs
    
    def format_health_report(self) -> str:
        """Format health report as readable string."""
        report = self.get_health_report()
        
        output = f"""
# Sync Health Report

**Status:** {'✅ HEALTHY' if report['healthy'] else '❌ UNHEALTHY'}
**State:** {report['state'].upper()}

## Metrics
- **Progress:** {report['metrics']['files_scanned']} / {report['metrics']['files_total']} ({report['metrics']['progress_percent']:.1f}%)
- **Speed:** {report['metrics']['files_per_second']:.2f} files/sec
- **Runtime:** {report['metrics']['runtime_seconds']:.1f} seconds
- **Last Progress:** {report['metrics']['time_since_progress']:.1f} seconds ago
- **Errors:** {report['metrics']['errors_count']}

## Watcher
- **Status:** {'ALIVE' if report['watcher']['alive'] else 'DEAD' if report['watcher']['exists'] else 'NOT STARTED'}

## Recent Errors
"""
        
        if report['errors']:
            for err in report['errors']:
                output += f"- [{err['timestamp']}] {err['type']}: {err['message']}\n"
        else:
            output += "- None\n"
        
        output += "\n## Recommendations\n"
        for rec in report['recommendations']:
            output += f"- {rec}\n"
        
        if report['recovery_attempts'] > 0:
            output += f"\n**Recovery Attempts:** {report['recovery_attempts']}\n"
        
        return output


# Example usage in MCP server
if __name__ == "__main__":
    import sys
    
    # Demo
    monitor = SyncHealthMonitor("/tmp/test_project")
    
    print("Starting scan...")
    if monitor.start_scan():
        print("Scan started successfully")
        
        # Simulate progress
        for i in range(0, monitor.metrics.files_total + 1, 10):
            monitor.update_scan_progress(i)
            time.sleep(0.1)
        
        print("\n" + monitor.format_health_report())
    else:
        print("Scan failed to start")
        print(monitor.format_health_report())

