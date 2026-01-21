import { useState, useEffect } from 'react'
import { Play, Square, RefreshCw, CheckCircle, XCircle, AlertTriangle } from 'lucide-react'

interface Provider {
  name: string
  type: 'local' | 'hosted'
  status: 'available' | 'unavailable' | 'configured' | 'not_configured'
  url: string
  description: string
  models?: string[]
}

interface LLMProviderSettingsProps {
  onChange: () => void
}

export default function LLMProviderSettings({ onChange }: LLMProviderSettingsProps) {
  const [providers, setProviders] = useState<Provider[]>([
    {
      name: 'ollama',
      type: 'local',
      status: 'available',
      url: 'http://localhost:11434',
      description: 'Local models via Ollama',
      models: ['llama3:8b', 'llama3:70b', 'codellama:13b']
    },
    {
      name: 'lmstudio',
      type: 'local',
      status: 'available',
      url: 'http://localhost:1234',
      description: 'Local models via LM Studio (OpenAI-compatible)',
      models: ['local-model-1', 'local-model-2']
    },
    {
      name: 'openai',
      type: 'hosted',
      status: 'configured',
      url: 'https://api.openai.com/v1',
      description: 'Hosted models via OpenAI API',
      models: ['gpt-4o', 'gpt-4-turbo', 'gpt-3.5-turbo']
    }
  ])

  const [selectedProvider, setSelectedProvider] = useState<string>('ollama')
  const [selectedModel, setSelectedModel] = useState<string>('llama3:8b')
  const [isLoading, setIsLoading] = useState(false)
  const [lastAction, setLastAction] = useState<string>('')

  const currentProvider = providers.find(p => p.name === selectedProvider)

  const handleRefreshProviders = async () => {
    setIsLoading(true)
    setLastAction('Refreshing provider status...')

    try {
      // Simulate API call to check provider status
      await new Promise(resolve => setTimeout(resolve, 2000))

      // Mock updated status
      setProviders(prev => prev.map(p => ({
        ...p,
        status: Math.random() > 0.2 ? 'available' : 'unavailable' as const
      })))

      setLastAction('Provider status refreshed')
      setTimeout(() => setLastAction(''), 3000)
    } catch (error) {
      setLastAction('Failed to refresh providers')
    } finally {
      setIsLoading(false)
    }
  }

  const handleLoadModel = async () => {
    setIsLoading(true)
    setLastAction(`Loading ${selectedModel}...`)

    try {
      await new Promise(resolve => setTimeout(resolve, 3000))
      setLastAction(`Successfully loaded ${selectedModel}`)
      setTimeout(() => setLastAction(''), 3000)
      onChange()
    } catch (error) {
      setLastAction(`Failed to load ${selectedModel}`)
    } finally {
      setIsLoading(false)
    }
  }

  const handleUnloadModel = async () => {
    setIsLoading(true)
    setLastAction(`Unloading ${selectedModel}...`)

    try {
      await new Promise(resolve => setTimeout(resolve, 2000))
      setLastAction(`Successfully unloaded ${selectedModel}`)
      setTimeout(() => setLastAction(''), 3000)
      onChange()
    } catch (error) {
      setLastAction(`Failed to unload ${selectedModel}`)
    } finally {
      setIsLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'available':
      case 'configured':
        return 'text-green-400'
      case 'unavailable':
        return 'text-red-400'
      case 'not_configured':
        return 'text-yellow-400'
      default:
        return 'text-gray-400'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'available':
      case 'configured':
        return <CheckCircle className="h-4 w-4" />
      case 'unavailable':
        return <XCircle className="h-4 w-4" />
      case 'not_configured':
        return <AlertTriangle className="h-4 w-4" />
      default:
        return <AlertTriangle className="h-4 w-4" />
    }
  }

  return (
    <div className="space-y-6">
      {/* Current Configuration */}
      <div className="card p-6">
        <h2 className="text-lg font-semibold mb-4">Current LLM Configuration</h2>

        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <label className="label">Active Provider</label>
            <select
              value={selectedProvider}
              onChange={(e) => {
                setSelectedProvider(e.target.value)
                setSelectedModel('')
                onChange()
              }}
              className="input w-full"
            >
              {providers.map(provider => (
                <option key={provider.name} value={provider.name}>
                  {provider.name} ({provider.type})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="label">Active Model</label>
            <select
              value={selectedModel}
              onChange={(e) => {
                setSelectedModel(e.target.value)
                onChange()
              }}
              className="input w-full"
              disabled={!currentProvider?.models?.length}
            >
              <option value="">Select a model...</option>
              {currentProvider?.models?.map(model => (
                <option key={model} value={model}>{model}</option>
              ))}
            </select>
          </div>
        </div>

        {lastAction && (
          <div className="mt-4 p-3 bg-muted/50 rounded-md">
            <div className="flex items-center text-sm">
              {isLoading && <RefreshCw className="h-4 w-4 mr-2 animate-spin" />}
              {lastAction}
            </div>
          </div>
        )}
      </div>

      {/* Provider Status */}
      <div className="card p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold">Provider Status</h2>
          <button
            onClick={handleRefreshProviders}
            disabled={isLoading}
            className="btn btn-outline btn-sm"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>

        <div className="grid gap-4">
          {providers.map(provider => (
            <div key={provider.name} className="flex items-center justify-between p-4 border border-border rounded-md">
              <div className="flex items-center space-x-3">
                <div className={getStatusColor(provider.status)}>
                  {getStatusIcon(provider.status)}
                </div>

                <div>
                  <div className="font-medium capitalize">{provider.name}</div>
                  <div className="text-sm text-muted-foreground">{provider.description}</div>
                  <div className="text-xs text-muted-foreground mt-1">
                    {provider.url} • {provider.type}
                  </div>
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <span className={`text-xs px-2 py-1 rounded-full ${
                  provider.status === 'available' || provider.status === 'configured'
                    ? 'bg-green-500/10 text-green-400'
                    : provider.status === 'unavailable'
                    ? 'bg-red-500/10 text-red-400'
                    : 'bg-yellow-500/10 text-yellow-400'
                }`}>
                  {provider.status.replace('_', ' ')}
                </span>

                {provider.models && provider.models.length > 0 && (
                  <span className="text-xs text-muted-foreground">
                    {provider.models.length} models
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Model Management */}
      {currentProvider?.type === 'local' && (
        <div className="card p-6">
          <h2 className="text-lg font-semibold mb-4">Model Management</h2>
          <p className="text-muted-foreground mb-6">
            Load and unload models for {currentProvider.name}. Local models need to be loaded into memory before use.
          </p>

          <div className="flex items-center space-x-4">
            <div className="flex-1">
              <label className="label">Model to Manage</label>
              <select
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className="input w-full"
                disabled={!currentProvider?.models?.length}
              >
                <option value="">Select a model...</option>
                {currentProvider?.models?.map(model => (
                  <option key={model} value={model}>{model}</option>
                ))}
              </select>
            </div>

            <div className="flex space-x-2 pt-6">
              <button
                onClick={handleLoadModel}
                disabled={!selectedModel || isLoading}
                className="btn btn-primary flex items-center"
              >
                <Play className="h-4 w-4 mr-2" />
                Load
              </button>

              <button
                onClick={handleUnloadModel}
                disabled={!selectedModel || isLoading}
                className="btn btn-outline flex items-center"
              >
                <Square className="h-4 w-4 mr-2" />
                Unload
              </button>
            </div>
          </div>
        </div>
      )}

      {/* API Configuration */}
      {currentProvider?.type === 'hosted' && (
        <div className="card p-6">
          <h2 className="text-lg font-semibold mb-4">API Configuration</h2>

          <div className="space-y-4">
            <div>
              <label className="label">API Key</label>
              <input
                type="password"
                placeholder={`Enter ${currentProvider.name.toUpperCase()} API key`}
                className="input w-full"
                onChange={onChange}
              />
              <p className="text-xs text-muted-foreground mt-1">
                Get your API key from{' '}
                <a
                  href={currentProvider.name === 'openai' ? 'https://platform.openai.com/api-keys' : '#'}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-accent hover:underline"
                >
                  {currentProvider.name}.com
                </a>
              </p>
            </div>

            <div>
              <label className="label">Custom API Base URL (Optional)</label>
              <input
                type="url"
                placeholder="https://api.openai.com/v1"
                className="input w-full"
                onChange={onChange}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
