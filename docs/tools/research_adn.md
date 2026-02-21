# AI Research & RAG (adn_research)

Unified portmanteau tool for AI research and knowledge discovery. This tool consolidates 15+ research and AI tools including web search, academic research, document ingestion, RAG queries, and LLM interactions into a single tool.

## Operations

| Operation | Description | Required Parameters |
|:---|:---|:---|
| `web_search` | Perform a web search | `query` |
| `arxiv` | Search academic papers on arXiv | `query` |
| `github` | Search code repositories on GitHub | `query` |
| `tvtropes` | Research narrative tropes on TV Tropes | `query` |
| `document_ingest`| Process and ingest a document into the RAG system| `path` |
| `rag_query` | Perform a RAG-enhanced AI query | `query` |
| `llm_config` | Configure LLM provider settings | `provider`, `model` |
| `llm_generate` | Generate content using configured LLM | `content` |
| `research_orchestrate`| Agentic research orchestration across multiple sources| `query` |

## Parameters

- `operation` (str): Research operation to perform.
- `query` (str, optional): Search query or research topic.
- `provider` (str, optional): AI provider (e.g., "openai", "anthropic", "google").
- `model` (str, optional): Model name/version.
- `api_key` (str, optional): API key for the provider.
- `limit` (int, optional): Maximum results to return (Default: 10).
- `language` (str, optional): Programming language filter for GitHub search.
- `path` (str, optional): File path for document processing.
- `content` (str, optional): Content for LLM generation operations.

## Examples

### Web search
```python
adn_research("web_search", query="machine learning transformers")
```

### Academic research
```python
adn_research("arxiv", query="neural networks", limit=10)
```

### GitHub code search
```python
adn_research("github", query="react hooks", language="typescript")
```

### Document processing
```python
adn_research("document_ingest", path="/path/to/document.pdf")
```

### RAG query
```python
adn_research("rag_query", query="explain quantum computing")
```

### Configure LLM
```python
adn_research("llm_config", provider="openai", model="gpt-4", api_key="sk-...")
```
