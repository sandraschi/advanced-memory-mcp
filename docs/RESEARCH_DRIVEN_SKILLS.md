# Research-Driven Skills: MCP 2.14.3 + Web Search Integration

## Overview

**Research-Driven Skills** combine FastMCP 2.14.3 sampling capabilities with real-time web search to create skills based on current, time-critical information. This enables creation of specialized skills for rapidly evolving topics like medical research, political developments, and conspiracy analysis.

## Architecture

### Components

1. **`make_skill_advanced`** - FastMCP 2.14.3 sampling tool for LLM interrogation
2. **`adn_web_search`** - Structured web search with multiple providers
3. **Client LLM** (Gemini 3 Fast, Claude, etc.) - Intelligent content generation
4. **Research Pipeline** - Automated web research and content integration

### Data Flow

```
Topic Input → Web Research → LLM Analysis → Skill Generation → Validation → Output
     ↓            ↓            ↓            ↓            ↓            ↓
"brain tumor" → Search APIs → Gemini 3 → Structured → Quality → SKILL.md
                     ↑                        Content     Checks
                Current Research            Generation
```

## Key Features

### 🕵️ **Intelligent Research**

- **Multiple Search Providers**: DuckDuckGo (free), SerpApi (Google), Bing Web Search
- **Time-Based Filtering**: Latest research from hours to years
- **Source Filtering**: Domain-specific results (NIH, Reuters, Snopes, etc.)
- **Relevance Scoring**: Automated quality assessment

### 🧠 **LLM Integration**

- **FastMCP 2.14.3 Sampling**: Direct client LLM interrogation
- **Structured Output**: Pydantic models for consistent results
- **Iterative Refinement**: Multi-pass improvement cycles
- **Context Preservation**: Maintains research context throughout

### 📚 **Primary Source Document Analysis**

- **Document Ingestion**: Read books, PDFs, academic papers, historical texts
- **Text Extraction**: Support for PDF, EPUB, TXT, MD formats
- **Passage Quoting**: Include direct quotes from original sources
- **Deep Analysis**: Multi-chunk processing for comprehensive understanding

### 📄 **Academic Research (arXiv)**

- **arXiv Integration**: Search and analyze academic preprints
- **Peer-Reviewed Content**: Access cutting-edge research before publication
- **Field-Specific Search**: Target specific academic disciplines
- **Citation Analysis**: Track research impact and relationships
- **Trend Analysis**: Identify emerging research directions

### 🎭 **Narrative Analysis (TV Tropes)**

- **TV Tropes Integration**: Research storytelling patterns and archetypes
- **Character Archetypes**: Study personality types and character development
- **Plot Structures**: Analyze narrative frameworks and story patterns
- **Genre Conventions**: Understand media-specific tropes and expectations
- **Creative Writing**: Research narrative techniques and audience expectations
- **⚠️ Compliance**: Respects TV Tropes terms - no scraping, manual verification required

### 🧠 **RAG (Retrieval Augmented Generation)**

- **Vector Embeddings**: ChromaDB-powered semantic search
- **Intelligent Chunking**: Fixed-size, sentence-based, and semantic chunking
- **Persistent Knowledge**: Vector database for long-term knowledge storage
- **Context-Aware Retrieval**: Find relevant content across large documents
- **Large Document Support**: Process books and papers beyond LLM context limits

### 📊 **Specialized Use Cases**

#### Medical Research Skills
```javascript
await make_skill_advanced({
  operation: "research_driven_skill",
  topic: "brain tumor glioblastoma expert",
  web_search_provider: "auto",
  web_search_time_filter: "year",
  web_sources_filter: ["nih.gov", "mayo.edu", "cancer.gov"]
})
```

**Generated Content Includes:**
- Latest clinical trials and treatment advances
- New drug approvals and research breakthroughs
- Current survival statistics and prognosis data
- Emerging immunotherapy and targeted therapies

#### Political Analysis Skills
```javascript
await make_skill_advanced({
  operation: "research_driven_skill",
  topic: "Trump Greenland complications expert",
  web_search_provider: "bing",
  web_search_time_filter: "month",
  web_sources_filter: ["reuters.com", "bbc.com", "wsj.com"]
})
```

**Generated Content Includes:**
- Current legal developments and court rulings
- Recent news coverage and analysis
- Financial implications and market reactions
- Political fallout and stakeholder responses

#### Conspiracy Debunking Skills
```javascript
await make_skill_advanced({
  operation: "research_driven_skill",
  topic: "Kennedy assassination mahadebunking expert",
  web_search_provider: "serpapi",
  web_search_time_filter: "any",
  web_sources_filter: ["snopes.com", "factcheck.org", "wikipedia.org"]
})
```

**Generated Content Includes:**
- Latest historical research and declassified documents
- Current fact-checking analyses
- Expert consensus and academic findings
- Common myths and their debunking evidence

#### Primary Source Document Analysis
```javascript
await make_skill_advanced({
  operation: "research_driven_skill",
  topic: "Daniel Paul Schreber psychological case study expert",
  source_documents: ["/books/schreber-memoirs.pdf"],
  focus_topics: ["delusions", "paranoia", "divine_mission"]
})
```

**Generated Content Includes:**
- Direct quotes from Schreber's actual memoirs
- Analysis of specific delusional passages
- Historical context from the primary source
- Authentic psychological insights from original text

#### Historical Text Analysis
```javascript
await make_skill_advanced({
  operation: "research_driven_skill",
  topic: "Malleus Maleficarum witchcraft theology expert",
  source_documents: ["/books/malleus-maleficarum.pdf"],
  web_search_provider: "auto",
  web_search_time_filter: "any"
})
```

**Generated Content Includes:**
- Direct passages from the 15th-century witchcraft manual
- Analysis of Inquisitorial theology and practices
- Medieval demonology concepts from primary source
- Historical context and interpretations

#### Academic Paper Analysis
```javascript
await make_skill_advanced({
  operation: "research_driven_skill",
  topic: "Transformer architecture deep learning expert",
  source_documents: ["/papers/attention-is-all-you-need.pdf"],
  web_search_provider: "auto",
  web_search_time_filter: "year",
  web_sources_filter: ["arxiv.org", "neuralips.cc"]
})
```

**Generated Content Includes:**
- Direct quotes from the original Vaswani et al. paper
- Mathematical formulations from the source
- Implementation details and intuitions
- Current developments building on the original work

#### Academic Research Integration
```javascript
await make_skill_advanced({
  operation: "research_driven_skill",
  topic: "quantum machine learning expert",
  source_documents: ["/papers/quantum-ml-survey.pdf"],
  web_search_provider: "auto",
  web_search_time_filter: "year",
  enable_web_search: true  // Includes arXiv research
})
```

**Generated Content Includes:**
- Latest quantum ML research from arXiv preprints
- Theoretical foundations from recent papers
- Implementation approaches from academic research
- Citation of peer-reviewed methodologies

#### Narrative & Creative Writing Skills
```javascript
await make_skill_advanced({
  operation: "research_driven_skill",
  topic: "creative writing character development expert",
  web_search_provider: "auto",
  enable_web_search: true  // Includes TV Tropes research
})
```

**Generated Content Includes:**
- Character archetypes and personality patterns from TV Tropes
- Narrative structures and plot frameworks
- Storytelling techniques and audience expectations
- Genre conventions and trope awareness
- ⚠️ TV Tropes content requires manual verification

#### Interdisciplinary Academic Research
```javascript
await make_skill_advanced({
  operation: "research_driven_skill",
  topic: "computational biology algorithms expert",
  web_search_provider: "auto",
  web_search_time_filter: "year",
  enable_web_search: true
})
```

**Generated Content Includes:**
- Recent bioinformatics algorithms from arXiv
- Computational approaches to biological problems
- Statistical methods for biological data analysis
- Integration of ML techniques in computational biology

## Configuration

### Environment Variables

```bash
# Web Search API Keys (optional - DuckDuckGo works without keys)
SERPAPI_API_KEY=your_serpapi_key
BING_API_KEY=your_bing_key

# Document Processing Dependencies
pip install PyMuPDF  # For PDF processing
pip install ebooklib  # For EPUB processing (future enhancement)

# RAG System Dependencies
pip install chromadb  # Vector database
pip install sentence-transformers  # Embedding models

# RAG Configuration (optional)
RAG_PERSIST_DIR=./chroma_db  # Vector database location
RAG_EMBEDDING_MODEL=all-MiniLM-L6-v2  # Embedding model
RAG_CHUNK_SIZE=1000  # Chunk size in characters
RAG_CHUNK_OVERLAP=200  # Chunk overlap

# FastMCP Sampling (configured automatically)
# Uses client's LLM (Gemini 3 Fast, Claude, etc.)
```

### IDE Integration

#### Windsurf Configuration
```json
{
  "mcpServers": {
    "advanced-memory": {
      "command": "python",
      "args": ["-m", "advanced_memory.mcp.server"],
      "env": {
        "ADVANCED_MEMORY_FULL_TOOLS_MODE": "true"
      }
    }
  }
}
```

#### Cursor Configuration
```json
{
  "mcpServers": {
    "advanced-memory": {
      "command": "python",
      "args": ["-m", "advanced_memory.mcp.server"]
    }
  }
}
```

## Usage Examples

### Complete Research-Driven Skill Creation

```javascript
// Create a brain tumor expert skill with current research
const result = await make_skill_advanced({
  operation: "research_driven_skill",
  topic: "glioblastoma multiforme treatment expert",
  target_quality: "expert",
  web_search_provider: "auto",
  web_search_time_filter: "year",
  web_sources_filter: ["nih.gov", "asco.org", "nature.com"]
});

console.log("Skill created:", result.output_path);
console.log("Research sources used:", result.research_sources_used);
```

### Primary Source Document Analysis

```javascript
// Create Schreber expert from his actual memoirs (with RAG)
const schreberSkill = await make_skill_advanced({
  operation: "research_driven_skill",
  topic: "Daniel Paul Schreber psychological analysis expert",
  source_documents: ["/books/schreber-memoirs.pdf"],
  focus_topics: ["delusions", "paranoia", "divine_mission", "mental_illness"]
});

console.log("Schreber skill created with RAG processing:", schreberSkill.document_sources_used, "documents");
```

### Direct RAG Operations

```javascript
// Ingest documents into RAG system for later querying
await adn_rag("ingest_document", document_path="/books/malleus-maleficarum.pdf");

// Query across all ingested documents
const witchcraftResults = await adn_rag("query_knowledge", query="witchcraft theology medieval beliefs");

// Search within specific documents
const schreberDelusions = await adn_rag(
  "query_knowledge",
  query="divine mission delusions",
  document_filter=["_books_schreber-memoirs.pdf"]
);

// List all documents in knowledge base
const allDocs = await adn_rag("list_documents");

// Get detailed document information
const docInfo = await adn_rag("get_document_info", document_id="_papers_attention-is-all-you-need.pdf");
```

```javascript
// Analyze Malleus Maleficarum with both primary text and historical research
const malleusSkill = await make_skill_advanced({
  operation: "research_driven_skill",
  topic: "Malleus Maleficarum witchcraft theology expert",
  source_documents: ["/books/malleus-maleficarum.pdf"],
  web_search_provider: "auto",
  web_search_time_filter: "any",
  web_sources_filter: ["britannica.com", "history.com", "wikipedia.org"]
});
```

```javascript
// Transformer expert with original paper + current developments
const transformerSkill = await make_skill_advanced({
  operation: "research_driven_skill",
  topic: "Transformer neural networks architecture expert",
  source_documents: ["/papers/attention-is-all-you-need.pdf"],
  web_search_provider: "auto",
  web_search_time_filter: "year",
  web_sources_filter: ["arxiv.org", "neuralips.cc", "openai.com"]
});

// Direct arXiv research for quantum computing
const arxivResults = await adn_arxiv_research({
  operation: "search_papers",
  query: "quantum supremacy experimental",
  category: "quant-ph",
  max_results: 15,
  sort_by: "submittedDate"
});

// Research character archetypes for writing (TV Tropes)
const characterArchetypes = await adn_tvtropes_research({
  operation: "character_archetypes",
  query: "mentor figures in fiction",
  max_results: 8
});

// Analyze narrative patterns
const narrativePatterns = await adn_tvtropes_research({
  operation: "narrative_analysis",
  query: "hero's journey structure",
  max_results: 5
});
```

### Multi-Iteration Enhancement

```javascript
// Start with basic research, then iteratively improve
const skill = await make_skill_advanced({
  operation: "research_driven_skill",
  topic: "cryptocurrency regulation expert",
  web_search_provider: "serpapi",
  web_search_time_filter: "month"
});

// Then enhance with additional iterations
const enhanced = await make_skill_advanced({
  operation: "iterative_improvement",
  existing_skill_path: skill.output_path,
  max_iterations: 3,
  enhancement_focus: ["examples", "practical", "references"]
});
```

### Custom Research Queries

The system automatically generates targeted research queries:

**For Medical Topics:**
- "glioblastoma latest treatments 2024"
- "brain tumor clinical trials new drugs"
- "glioblastoma immunotherapy advances current"

**For Political Topics:**
- "Trump Greenland complications latest news"
- "Greenland Trump real estate issues current status"
- "Trump Greenland investment problems recent"

**For Conspiracy Analysis:**
- "Kennedy assassination conspiracy debunking evidence"
- "JFK assassination latest research and analysis"
- "Kennedy conspiracy theories fact checking current"

## Output Format

### Generated SKILL.md Structure

```yaml
---
name: brain-tumor-glioblastoma-expert
description: Current expert knowledge on glioblastoma treatment based on latest research
category: medical
version: 1.0.0
last_researched: 2025-12-02
research_sources: 15
---

# Brain Tumor Glioblastoma Expert

## Current Research & Developments

[Latest research findings from web search]

## Treatment Landscape 2024

[Current treatment options and breakthroughs]

## Clinical Trials & Emerging Therapies

[Recent clinical trial results and new drugs]

## References

[Links to research sources and medical resources]
```

## Document Format Support

### Supported Formats
- **PDF**: Books, academic papers, research articles (recommended)
- **Text Files**: .txt, .md files with plain text content
- **EPUB**: E-book format (basic support, enhanced in future versions)

### Document Processing Features
- **Text Extraction**: Automatic text extraction from all supported formats
- **Chunking**: Intelligent document chunking for analysis
- **Quote Detection**: Automatic identification of notable passages
- **Metadata Extraction**: Title, author, page count, word count
- **Theme Analysis**: Automatic theme and topic identification

## RAG System Architecture

### Components
- **ChromaDB**: Vector database for embeddings storage
- **Sentence Transformers**: Embedding model for semantic similarity
- **Intelligent Chunking**: Multiple chunking strategies (fixed, sentence, semantic)
- **Query Processing**: Semantic search with relevance scoring
- **Document Management**: Full CRUD operations for document collections

### RAG Operations
- **ingest_document**: Process and vectorize documents
- **query_knowledge**: Semantic search across all documents
- **list_documents**: Browse document collections
- **get_document_info**: Document metadata and statistics
- **delete_document**: Remove documents and clean up vectors
- **search_similar**: Find semantically similar content

### Chunking Strategies
- **Fixed**: Overlapping windows of fixed character count
- **Sentence**: Group by sentence boundaries
- **Semantic**: Content-aware chunking (future enhancement)

## Performance & Limitations

### Strengths
- ✅ **Current Information**: Always uses latest available data
- ✅ **Multiple Sources**: Cross-references information from authoritative sources
- ✅ **Primary Source Depth**: Direct analysis of original documents and books
- ✅ **Academic Research Access**: Direct integration with arXiv preprints and papers
- ✅ **RAG-Powered Retrieval**: Semantic search across large document collections
- ✅ **Persistent Knowledge**: Vector database for long-term knowledge storage
- ✅ **Context Window Freedom**: Process documents larger than LLM limits
- ✅ **Structured Output**: Consistent, professional skill format
- ✅ **Flexible Research**: Adapts queries based on topic type

### Limitations
- ⚠️ **API Dependencies**: Requires web search API keys for best results
- ⚠️ **Rate Limits**: Search APIs have usage limits
- ⚠️ **RAG Dependencies**: ChromaDB and embedding models required
- ⚠️ **Document Size**: Large documents may take time to process
- ⚠️ **Text Quality**: OCR-scanned PDFs may have extraction errors
- ⚠️ **Vector Storage**: Requires disk space for embeddings
- ⚠️ **TV Tropes Compliance**: Strict terms of service - manual verification required
- ⚠️ **Time Sensitive**: Skills may become outdated as research evolves

## Troubleshooting

### Common Issues

**"No research data available"**
- Check web search provider configuration
- Verify API keys for paid providers
- Try different search provider

**"Document processing failed"**
- Verify document file exists and is readable
- Check document format is supported (PDF, TXT, MD, EPUB)
- Ensure file is not password-protected
- Try with a smaller document first

**"No text extracted from document"**
- Document may be image-based (try OCR preprocessing)
- File may be corrupted or in unsupported format
- Check file encoding for text documents

**"RAG system not available"**
- Check ChromaDB installation: `pip install chromadb`
- Verify sentence-transformers: `pip install sentence-transformers`
- Ensure write permissions for RAG_PERSIST_DIR
- Check embedding model availability

**"Vector search failed"**
- Verify RAG system initialization
- Check document was properly ingested
- Try different chunking method
- Ensure query is not too short or generic

**"Sampling client not available"**
- Ensure FastMCP 2.14.3 is installed
- Check MCP server configuration
- Verify LLM provider is configured

**"Skill generation failed"**
- Check topic is specific enough
- Try simplifying the topic
- Use different web search provider
- Verify source documents are properly formatted

**"TV Tropes access blocked"**
- TV Tropes has aggressive anti-bot measures
- Respect rate limits (2-5 second delays implemented)
- For serious research, visit tvtropes.org manually
- Tool provides guidance, not scraped content
- Consider ethical implications of automated access

### Debug Mode

Enable detailed logging:
```bash
export LOG_LEVEL=DEBUG
# Restart MCP server
```

## research_first_create (Research-Chain-First)

**research_first_create** uses the chained research pipeline (adn_skills_research) plus LLMClient to create skills without MCP sampling. Flow: run_chain -> LLM SKILL.md -> scaffold_skill + scaffold_references_from_research -> validate_skill_agentskills.

### Parameters
- **topic** (required): Research topic
- **skill_name** (optional): Hyphen-case name; derived from topic if omitted
- **output_path** (optional): Directory or parent path for skill output
- **research_sources**: ["web", "arxiv", "github", "rag"] (default)
- **max_research_iterations**: 1-5 (default 3)
- **enable_review_loop**: If true and spec validation fails, LLM attempts one fix pass

### Example
```javascript
const result = await make_skill_advanced({
  operation: "research_first_create",
  topic: "FastMCP 2.14 agentic workflows",
  skill_name: "fastmcp-agentic-workflows",
  research_sources: ["web", "arxiv", "github", "rag"],
  max_research_iterations: 3,
  enable_review_loop: true,
  output_path: "./skills"
});

console.log("Skill path:", result.skill_path);
console.log("Spec compliant:", result.spec_compliant);
```

### Output
Returns: success, skill_path, skill_name, references_path, spec_compliant, spec_warnings, agentskills_checks, review_loop_applied, coverage_score, iteration_count, sources_used.

## Future Enhancements

### Implementation Plan

See [ADN_SKILLS_DEEP_RESEARCH_IMPLEMENTATION_PLAN.md](https://github.com/sandraschi/mcp-central-docs/blob/main/docs/skills/ADN_SKILLS_DEEP_RESEARCH_IMPLEMENTATION_PLAN.md) in mcp-central-docs for the detailed plan. Implemented:
- Research chaining (arxiv, github, rag, web in configurable pipelines)
- LLM-guided loop (gap analysis, next-source decisions along the path)
- Reference scaffolding (auto-populate references/ from research)
- Spec validation (agentskills.io compliance)
- Research-first creator mode (research_first_create operation)

### Planned Features
- **Multi-LLM Comparison**: Generate skills using multiple LLMs for comparison
- **Automated Updates**: Skills that can self-update with new research
- **Source Credibility Scoring**: Weight sources by academic/factual credibility
- **Collaborative Research**: Multi-user research contribution system

### Integration Possibilities
- **Academic Databases**: PubMed, IEEE Xplore, JSTOR integration
- **News APIs**: Direct integration with news organizations
- **Social Media Analysis**: Research from X/Twitter, Reddit, etc.
- **Expert Networks**: Direct consultation with domain experts

## Migration from Manual Skills

If you were manually creating skills:

1. **Switch to research-driven creation** for time-sensitive topics
2. **Use web search integration** for current information
3. **Configure preferred search providers** in your environment
4. **Set up domain filters** for authoritative sources

This approach provides skills that are always current and backed by the latest research and developments.
