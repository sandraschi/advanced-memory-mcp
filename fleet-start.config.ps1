# Per-repo fleet start config for advanced-memory-mcp
@{
    Name         = 'advanced-memory-mcp'
    BackendPort  = 10705
    FrontendPort = 10704
    HealthPath   = '/api/v1/health'
    WebRoot      = 'D:\Dev\repos\advanced-memory-mcp\webapp\frontend'
    NssmService  = 'advanced-memory-mcp'
    Backend = @{
        Kind = 'nssm'
    }
    Frontend = @{
        Kind           = 'vite-npm'
        PackageManager = 'npm'
        PortEnvVar     = 'VITE_PORT'
        ApiTargetEnv   = 'VITE_API_TARGET'
    }
}
