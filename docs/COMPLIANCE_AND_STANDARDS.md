# Advanced Memory MCP - Compliance & Standards (v14.1.0)

## Certification Status: GOLD STANDARD

This repository is monitored and validated as a **Production/Industrialized** component of the Alsergrund Bridge fleet.

### SOTA v14.1.0 Compliance Checklist

| Standard | Status | Implementation Details |
| :--- | :--- | :--- |
| **FastMCP 3.2** | ✅ | Native async orchestration with tool sampling. |
| **Ruff SOTA v14.1** | ✅ | 100% pass rate on security and linting gates. |
| **Arcade Compliance** | ✅ | Shadow Unrolling implemented to satisfy legacy scanners. |
| **Benny Protocol** | ✅ | Integrated emotional grounding and manual interrupt triggers. |
| **Industrial Justfile** | ✅ | v1.7.0 dashboard with precise operational recipes. |
| **Zero-Install (mcpb)** | ✅ | Officially validated `.mcpb` packaging support. |

## Versioning Philosophy

Advanced Memory follows a dual-track versioning system:
1. **Technical Version (1.7.0)**: Tracks the package lifecycle, dependencies, and functional fixes.
2. **Standard Version (SOTA v14.1.0)**: Tracks compliance with the wider fleet architecture and agentic behavioral standards.

## Security Hardening

- **Subprocess Isolation**: All external commands (e.g., Pandoc) are executed via hardened wrappers to prevent shell injection.
- **Port Locking**: Strict port allocation (10704/10705) with automated zombie process suppression.
- **Data Privacy**: Local-first architecture; metadata and vectors never leave the 9th District unless explicitly exported by the user.

---

[Back to README](../README.md) | [Fleet Integration](FLEET.md) | [Usage Guide](USAGE.md)
