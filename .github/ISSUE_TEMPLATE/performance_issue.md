---
name: Performance Issue
about: Report performance problems with Advanced Memory MCP
title: '[PERFORMANCE] '
labels: ['performance', 'needs-triage']
assignees: ''
---

## 🐌 Performance Problem
Describe the performance issue you're experiencing.

## 📊 Performance Metrics
Please provide specific metrics where possible:

### Response Times
- Tool execution time: [e.g., 5+ seconds for simple operations]
- Search time: [e.g., 10+ seconds for basic queries]
- Import/Export time: [e.g., 30+ minutes for 1000 notes]
- Sync time: [e.g., 2+ minutes for small changes]

### Resource Usage
- CPU usage: [e.g., 50%+ during operations]
- Memory usage: [e.g., 500MB+ RAM]
- Disk I/O: [e.g., High disk activity]
- Network usage: [if applicable]

## 🔄 Steps to Reproduce
1. Go to '...'
2. Click on '....'
3. Execute operation '....'
4. Observe slow performance

## 📈 Expected Performance
Describe what performance you expected:
- Tool execution: [e.g., < 1 second]
- Search: [e.g., < 2 seconds]
- Import/Export: [e.g., < 5 minutes]

## 🖥️ Environment
**System Information:**
 - OS: [e.g. Windows 10, macOS 12.0, Ubuntu 20.04]
 - CPU: [e.g., Intel i7-12700K, Apple M1 Pro]
 - RAM: [e.g., 16GB, 32GB]
 - Storage: [e.g., SSD, NVMe, HDD]
 - Claude Desktop Version: [e.g. 1.0.0]
 - Advanced Memory MCP Version: [e.g. 1.0.0]

**Project Details:**
 - Number of notes: [e.g., 1000+]
 - Project size: [e.g., 500MB]
 - File types: [e.g., mostly markdown, some images]
 - Folder structure: [e.g., deeply nested, flat]

## 📸 Performance Screenshots
If applicable, add screenshots of:
- Task Manager/Activity Monitor showing resource usage
- Claude Desktop performance indicators
- Timing measurements

## 🔍 Diagnostic Information
Please include:

### System Status
```python
# Run this and include output
adn_navigation("status", level="detailed")
```

### Sync Status
```python
# Run this and include output
adn_navigation("sync_status")
```

### Recent Activity
```python
# Run this and include output
adn_navigation("recent_activity", timeframe="1d")
```

## 📋 Additional Context
- When did the performance issue start?
- Does it affect all operations or specific ones?
- Have you noticed any patterns (time of day, specific operations)?
- Any recent changes to your system or project?

## 🎯 Priority
- [ ] Critical (system unusable)
- [ ] High (significantly impacts workflow)
- [ ] Medium (noticeable but manageable)
- [ ] Low (minor inconvenience)

## 📝 Additional Information
- [ ] Performance was better in previous versions
- [ ] Issue affects multiple users
- [ ] I can provide a minimal reproduction case
- [ ] I have performance monitoring data
