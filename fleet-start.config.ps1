# Per-repo fleet start config for advanced-memory-mcp
# Edit ports/backend target here - start.ps1 is fleet-standard.
@{
    Name         = 'advanced-memory-mcp'
    BackendPort  = 10705
    FrontendPort = 10704
    HealthPath   = '/api/v1/health'
    WebRoot      = 'webapp\frontend'
    Backend = @{
        Kind          = 'uvicorn'
        UvicornTarget = 'advanced_memory.server:app'
        Env           = @{ WEB_PORT = '10705' }
    }
    Frontend = @{
        Kind           = 'vite-npm'
        PackageManager = 'npm'
        PortEnvVar     = 'VITE_PORT'
        ApiTargetEnv   = 'VITE_API_TARGET'
    }
}
