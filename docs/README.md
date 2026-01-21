# Advanced Memory MCP Documentation
**Version**: 1.1.0b2
**Last Updated**: 2025-12-20
**Status**: SOTA Active - Dual STT Integration

---

## Purpose

This documentation provides comprehensive guidance for Advanced Memory MCP, a local-first knowledge management system with MCP protocol integration. Documentation is organized according to SOTA MCP Standards v12.0.

## 🏗️ SOTA Compliance

Advanced Memory MCP achieves **SOTA (State Of The Art)** compliance through:

### **The Three Pillars of SOTA Compliance**

1. **Architecture**: FastMCP 2.14.3 Cooperative pattern with portmanteau tool consolidation
2. **Behavior**: AI-optimized docstrings and conversational response patterns
3. **Operations**: Complete lifecycle management with persistent storage

---

## 📚 Documentation Structure

### **User-Facing Documentation**

#### [user-guide/](user-guide/)
Complete user guides for all features and workflows:

- **Getting Started**: Installation and basic usage
- **Core Concepts**: Knowledge graphs, zettelkasten, and observations
- **Tools Reference**: Complete guide to all 56 MCP tools
- **Integration Guides**: Claude Desktop, external services
- **Troubleshooting**: Common issues and solutions

#### [examples/](examples/)
Practical examples and demonstrations:
- Mermaid diagram examples
- Knowledge graph visualizations
- Export format samples

### **Developer Documentation**

#### [architecture/](architecture/)
System design and technical architecture:
- Portmanteau tools design rationale
- Database schema and relationships
- MCP protocol implementation
- Audio Soul 2026 architecture
- Claude Skills integration patterns

#### [SKILL_PARSING_ARCHITECTURE.md](SKILL_PARSING_ARCHITECTURE.md)
Skill discovery and parsing system:
- IDE skill directory locations
- YAML frontmatter parsing
- Skill discovery algorithms
- Error handling and validation

#### [development/](development/)
Contributing and development guides:
- FastMCP 2.14.3 migration guide
- Testing strategies and patterns
- Code standards and linting
- CI/CD pipeline documentation

#### [testing/](testing/)
Comprehensive testing documentation:
- Test organization and patterns
- Integration testing strategies
- Performance testing guides
- Quality assurance procedures

### **Integration & Deployment**

#### [integrations/](integrations/)
External service integrations:
- **Dual STT Architecture**: ikubaysan voice pipeline integration
- **Multi-Provider LLM**: Ollama, LM Studio, OpenAI, Anthropic, Gemini
- **MyVRWorlds**: React Tailwind VR control center
- **VR MCP Ecosystem**: Avatar, Blender, VRChat, Resonite, OSC, Unity
- Claude Skills ecosystem
- Audio processing (Kokoro, faster-whisper, Google Cloud Speech)
- Export formats (PDF, HTML, Docsify)
- Import sources (Evernote, Notion, OneNote)

#### [operations/](operations/)
Production deployment and operations:
- Docker containerization
- Monitoring and observability
- Backup and recovery
- Performance optimization

### **Specialized Documentation**

#### [github/](github/)
GitHub integration and automation:
- CI/CD workflows
- Release management
- Issue and PR automation
- Repository maintenance

#### [export/](export/)
Content export capabilities:
- PDF generation (native and Pandoc)
- HTML documentation sites
- Archive formats and migration
- Multi-format publishing

## 🔍 Quick Reference

### **For Users**
- **[Getting Started](user-guide/DEEPLINK_INSTALLATION.md)**: One-click installation
- **[Tools Reference](TOOLS_REFERENCE.md)**: Complete tool documentation
- **[Troubleshooting](TROUBLESHOOTING_GUIDE.md)**: Common issues and fixes

### **For Developers**
- **[Architecture](architecture/)**: System design and patterns
- **[Development](development/)**: Contributing guidelines
- **[Testing](testing/)**: Quality assurance procedures

### **For Operators**
- **[Operations](operations/)**: Deployment and maintenance
- **[Monitoring](operations/monitoring.md)**: System observability
- **[Security](SECURITY.md)**: Security considerations

## 📋 Documentation Standards

### **SOTA Compliance Requirements**

All documentation follows MCP Standards v12.0:

#### **1. Complete Coverage**
- Document all 56 tools, not just "main" features
- No TODO placeholders in public documentation
- Cover basic to advanced usage scenarios

#### **2. Clear Communication**
- Write for target audiences (users/developers/operators)
- Use concrete examples over abstract descriptions
- Progressive disclosure (simple → advanced)

#### **3. Technical Accuracy**
- Synchronize docs with code implementation
- Test all examples before committing
- Version compatibility specifications
- Regular freshness audits

### **Formatting Standards**

#### **Structure Patterns**
```markdown
# Title (H1)
**Version**: x.x.x
**Last Updated**: YYYY-MM-DD
**Status**: Active/SOTA

---

## Purpose
Brief description of document purpose.

## Sections
Content organized by clear headings.
```

#### **Code Examples**
- Include runnable examples for all features
- Specify version compatibility
- Test examples in CI/CD pipeline

#### **Cross-References**
- Link related documentation sections
- Maintain reference integrity
- Update links during refactoring

## 🔧 Maintenance

### **Documentation Freshness**
- Automated freshness audits monthly
- Version compatibility verification
- Community contribution guidelines

### **Quality Assurance**
- Technical review for all changes
- User testing for new features
- Accessibility and clarity reviews

---

**Need Help?**
- **Users**: Start with [user-guide/README.md](user-guide/README.md)
- **Developers**: See [development/README.md](development/README.md)
- **Operators**: Check [operations/README.md](operations/README.md)
- **Issues**: [GitHub Issues](https://github.com/sandraschi/advanced-memory-mcp/issues)
