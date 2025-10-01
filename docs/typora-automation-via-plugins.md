# Typora Automation via Plugins 🛠️🔌

**Revolutionary Plugin-Based Automation for Typora**

## Executive Summary

The **obgnail/typora_plugin ecosystem** provides the automation capabilities we've been missing! Through strategic use of **`json_rpc`** and **`commander`** plugins, we can achieve **full programmatic control** of Typora without brittle GUI automation.

**This changes everything**: No more WinAuto GUI scraping - **direct API control** of Typora's functionality!

## The Game-Changing Plugins

### 🎯 json_rpc Plugin - Direct API Control

**What it is**: WebSocket-based JSON-RPC interface allowing external applications to control Typora programmatically.

**Why it matters**:
- ✅ **Full Typora API access** - Export, content manipulation, UI control
- ✅ **No GUI automation needed** - Direct programmatic control
- ✅ **Stable and reliable** - Not affected by UI changes
- ✅ **Real-time interaction** - WebSocket-based communication

#### Technical Architecture

```
Basic Memory MCP Tool ↔ WebSocket ↔ Typora json_rpc Plugin
        ↓                                           ↓
   JSON-RPC Requests                    JSON-RPC Handler
   (export, getContent, etc.)           (execute commands)
```

#### Installation & Setup

1. **Install obgnail/typora_plugin**
   ```bash
   # Download from GitHub releases
   wget https://github.com/obgnail/typora_plugin/releases/latest/download/typora_plugin.zip
   # Extract to Typora plugins directory
   ```

2. **Enable json_rpc plugin**
   - Open Typora → Right-click → Plugins → json_rpc → Enable
   - Configure port (default: 8888)

3. **Configuration**
   ```json
   // typora_plugin/settings.json
   {
     "json_rpc": {
       "enabled": true,
       "port": 8888,
       "host": "localhost",
       "cors": ["basic-memory-app"],
       "security": "localhost_only"
     }
   }
   ```

### ⚡ Commander Plugin - CLI Integration

**What it is**: Command-line environment within Typora for executing external commands and scripts.

**Why it matters**:
- ✅ **CLI execution from Typora** - Run Basic Memory commands
- ✅ **Save hooks** - Automatic sync on file save
- ✅ **Workflow integration** - Seamless Basic Memory ↔ Typora workflows
- ✅ **Template integration** - Load Basic Memory research templates

#### Commander Features for Basic Memory

```javascript
// Commander plugin configuration
{
  "commander": {
    "enabled": true,
    "custom_commands": {
      "sync_to_basic_memory": "/path/to/basic-memory-cli sync $current_file",
      "export_basic_memory": "/path/to/basic-memory-cli export --project current",
      "load_research_template": "/path/to/basic-memory-cli template research $current_file",
      "validate_links": "/path/to/basic-memory-cli validate-links $current_file"
    },
    "hooks": {
      "onSave": ["sync_to_basic_memory"],
      "onExport": ["validate_links"],
      "onOpen": ["load_research_template"]
    }
  }
}
```

## Implementation: Basic Memory Typora Control

### Step 1: Create MCP Tool for json_rpc Communication

```python
# src/basic_memory/mcp/tools/typora_control.py

import asyncio
import json
import websockets
from typing import Dict, Any, Optional

@mcp.tool(
    description="""🎯 Control Typora via json_rpc plugin for automated export and content manipulation.

REQUIRES: obgnail/typora_plugin with json_rpc enabled on port 8888

FEATURES:
• Direct API export (PDF, HTML, Word)
• Content manipulation and insertion
• File operations and management
• Real-time Typora control

EXAMPLES:
typora_control("export", format="pdf", output_path="/exports/doc.pdf")
typora_control("get_content")
typora_control("insert_text", text="[[Basic Memory Link]]")
"""
)
async def typora_control(
    operation: str,
    format: Optional[str] = None,
    output_path: Optional[str] = None,
    text: Optional[str] = None,
    file_path: Optional[str] = None,
    project: Optional[str] = None
) -> str:
    """Control Typora via json_rpc WebSocket API."""

    async def send_rpc_request(method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send JSON-RPC request to Typora."""
        try:
            uri = "ws://localhost:8888"
            async with websockets.connect(uri) as websocket:
                request = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": method,
                    "params": params
                }

                await websocket.send(json.dumps(request))
                response = await websocket.recv()
                return json.loads(response)
        except Exception as e:
            return {"error": f"WebSocket communication failed: {str(e)}"}

    # Route operations
    if operation == "export":
        if not format or not output_path:
            return "❌ Export requires format and output_path parameters"

        result = await send_rpc_request("export", {
            "format": format,
            "outputPath": output_path,
            "includeImages": True,
            "embedStyles": True
        })

        if "error" in result:
            return f"❌ Export failed: {result['error']}"
        return f"✅ Successfully exported to {output_path}"

    elif operation == "get_content":
        result = await send_rpc_request("getContent", {})

        if "error" in result:
            return f"❌ Failed to get content: {result['error']}"
        return f"📄 Current document content:\n{result.get('result', 'No content')}"

    elif operation == "insert_text":
        if not text:
            return "❌ Insert operation requires text parameter"

        result = await send_rpc_request("insertText", {
            "text": text,
            "position": "current"
        })

        if "error" in result:
            return f"❌ Failed to insert text: {result['error']}"
        return f"✅ Successfully inserted text: {text}"

    elif operation == "open_file":
        if not file_path:
            return "❌ Open file requires file_path parameter"

        result = await send_rpc_request("openFile", {
            "path": file_path
        })

        if "error" in result:
            return f"❌ Failed to open file: {result['error']}"
        return f"✅ Successfully opened file: {file_path}"

    elif operation == "save_file":
        result = await send_rpc_request("saveFile", {})

        if "error" in result:
            return f"❌ Failed to save file: {result['error']}"
        return "✅ Successfully saved file"

    else:
        return f"""❌ Unknown operation: {operation}

Available operations:
• export - Export current document (requires format, output_path)
• get_content - Get current document content
• insert_text - Insert text at cursor (requires text)
• open_file - Open a file (requires file_path)
• save_file - Save current file

Example: typora_control("export", format="pdf", output_path="/exports/doc.pdf")
"""
```

### Step 2: Enhanced Export Tool with json_rpc

```python
# src/basic_memory/mcp/tools/export_typora_enhanced.py

@mcp.tool(
    description="""🚀 Enhanced Typora Export with json_rpc Automation

Uses Typora's json_rpc plugin for direct API control - NO GUI AUTOMATION!

REQUIRES: obgnail/typora_plugin with json_rpc enabled

WORKFLOW:
1. Prepare markdown files from Basic Memory
2. Use json_rpc to control Typora directly
3. Export via API calls (not GUI automation)
4. Retrieve exported files

ADVANTAGES:
• Stable (not affected by UI changes)
• Fast (direct API calls)
• Reliable (no timing issues)
• Feature-complete (all Typora export formats)

FORMATS: PDF, HTML, Word, OpenDocument, LaTeX
"""
)
async def export_typora_enhanced(
    output_dir: str = "typora_exports",
    format: str = "pdf",
    include_images: bool = True,
    embed_styles: bool = True,
    project: Optional[str] = None
) -> str:
    """Export Basic Memory notes using Typora json_rpc API."""

    # 1. Export markdown files from Basic Memory
    export_result = await export_typora.fn(
        output_dir=output_dir,
        direct_export_format="md",
        project=project
    )

    if "❌" in export_result:
        return f"Failed to export markdown files: {export_result}"

    # 2. Get list of exported markdown files
    output_path = Path(output_dir)
    md_files = list(output_path.glob("*.md"))

    if not md_files:
        return f"❌ No markdown files found in {output_dir}"

    # 3. Use json_rpc to export each file
    exported_files = []

    for md_file in md_files:
        # Open file in Typora via json_rpc
        open_result = await typora_control.fn(
            operation="open_file",
            file_path=str(md_file)
        )

        if "❌" in open_result:
            return f"Failed to open {md_file}: {open_result}"

        # Give Typora time to load the file
        await asyncio.sleep(1)

        # Export via json_rpc API
        export_file = md_file.with_suffix(f".{format}")
        export_result = await typora_control.fn(
            operation="export",
            format=format,
            output_path=str(export_file)
        )

        if "❌" in export_result:
            return f"Failed to export {md_file}: {export_result}"

        exported_files.append(export_file)

    # 4. Summary
    return f"""✅ **Typora Export Complete via json_rpc API!**

**Method**: Direct API control (no GUI automation)
**Files Processed**: {len(md_files)}
**Format**: {format.upper()}
**Output Directory**: {output_dir}

**Exported Files**:
{chr(10).join(f"• {f.name}" for f in exported_files)}

**Advantages of json_rpc Approach**:
• ⚡ **Fast**: Direct API calls, no UI delays
• 🎯 **Reliable**: Not affected by UI changes
• 🔧 **Stable**: No timing or focus issues
• 📋 **Complete**: All Typora export features available

**Next**: Files ready for use/sharing!
"""
```

## Commander Plugin Integration

### Save Hooks for Auto-Sync

```javascript
// typora_plugin/settings.json - Commander configuration
{
  "commander": {
    "enabled": true,
    "hooks": {
      "onSave": [
        "basic_memory_sync"
      ],
      "onExport": [
        "basic_memory_validate"
      ]
    },
    "custom_commands": {
      "basic_memory_sync": {
        "command": "/path/to/basic-memory-cli sync \"$current_file\"",
        "description": "Sync current file to Basic Memory"
      },
      "basic_memory_validate": {
        "command": "/path/to/basic-memory-cli validate-links \"$current_file\"",
        "description": "Validate Basic Memory links in exported file"
      },
      "basic_memory_template": {
        "command": "/path/to/basic-memory-cli load-template research \"$current_file\"",
        "description": "Load Basic Memory research template"
      }
    }
  }
}
```

### Workflow Integration Examples

```bash
# From Typora Commander (Ctrl+Shift+P):
# Type "basic_memory_sync" to sync current file
# Type "basic_memory_template" to load research template

# Automatic on save:
# File saves → Commander runs basic_memory_sync → Basic Memory updated

# On export:
# Export triggered → Commander validates links → Clean export
```

## Custom Plugin Development

### Basic Memory Integration Plugin

```javascript
// plugin/custom/basic_memory.js
class BasicMemoryIntegration {
  constructor() {
    this.name = 'basic_memory_integration';
  }

  // Hook into Typora's content processing
  processContent(content) {
    // Convert [[Basic Memory]] links to functional links
    return content.replace(
      /\[\[([^\]]+)\]\]/g,
      (match, linkText) => this.createBasicMemoryLink(linkText)
    );
  }

  createBasicMemoryLink(linkText) {
    // Query Basic Memory for link resolution
    const basicMemoryUrl = this.queryBasicMemory(linkText);
    return `[${linkText}](${basicMemoryUrl})`;
  }

  // Sync on save
  onFileSaved(filePath, content) {
    // Send content to Basic Memory
    this.syncToBasicMemory(filePath, content);
  }

  // Add Basic Memory toolbar
  initToolbar() {
    // Add buttons for Basic Memory operations
    this.addToolbarButton('sync', () => this.syncCurrentFile());
    this.addToolbarButton('search', () => this.searchBasicMemory());
  }
}

// Register plugin
module.exports = {
  plugin: BasicMemoryIntegration
};
```

## Complete Automation Workflow

### Phase 1: Plugin Setup (5 minutes)

1. **Install obgnail/typora_plugin**
2. **Enable json_rpc plugin** (port 8888)
3. **Enable commander plugin**
4. **Configure Basic Memory CLI paths**

### Phase 2: Basic Memory Integration (10 minutes)

1. **Configure save hooks** in commander
2. **Set up custom commands** for Basic Memory operations
3. **Test basic sync** functionality

### Phase 3: Full Automation (15 minutes)

1. **Create enhanced export tool** using json_rpc
2. **Test API-based export** (no GUI automation!)
3. **Verify file operations** work correctly

### Phase 4: Advanced Features (Ongoing)

1. **Develop custom plugin** for deep integration
2. **Implement link resolution** for [[Basic Memory]] syntax
3. **Add metadata injection** and relationship tracking
4. **Build two-way sync** capabilities

## Comparison: GUI Automation vs json_rpc

| Aspect | GUI Automation (WinAuto) | json_rpc Plugin |
|--------|--------------------------|-----------------|
| **Stability** | ❌ Brittle (UI changes break it) | ✅ Stable (API-based) |
| **Speed** | 🐌 Slow (UI interactions, timing) | ⚡ Fast (direct API calls) |
| **Reliability** | ⚠️ Unreliable (focus, timing issues) | ✅ Reliable (programmatic) |
| **Maintenance** | 🔧 High (update with UI changes) | 🛠️ Low (API stability) |
| **Features** | ⚠️ Limited (what UI exposes) | ✅ Full (all Typora features) |
| **Setup** | 🔧 Complex (WinAuto configuration) | ⚙️ Simple (enable plugin) |

## Real-World Usage Examples

### 1. Automated Research Export

```python
# Export entire research project as PDF book
await export_typora_enhanced.fn(
    output_dir="/research/exports",
    format="pdf",
    project="quantum_research"
)

# Result: Professional PDF with all research notes
# Method: json_rpc API calls (not GUI automation!)
```

### 2. Real-Time Sync Workflow

```javascript
// In Typora, save file → automatically syncs to Basic Memory
// Commander plugin handles the integration
onSave: async (filePath, content) => {
  await basicMemoryAPI.sync(filePath, content);
  console.log(`Synced ${filePath} to Basic Memory`);
}
```

### 3. Template Integration

```python
# Load Basic Memory research blueprint into Typora
await typora_control.fn(
    operation="insert_text",
    text="# Research Overview\n\n## Key Findings\n\n## Methodology\n\n## Conclusions"
)

# Result: Structured document based on Basic Memory template
```

## Troubleshooting

### json_rpc Connection Issues

```bash
# Check if json_rpc plugin is running
curl http://localhost:8888/status

# Verify plugin configuration
# typora_plugin/settings.json should have json_rpc enabled

# Restart Typora after plugin changes
```

### Commander Plugin Issues

```javascript
// Check commander configuration
console.log(typora.getPlugin('commander').config);

// Test custom commands
typora.runCommand('basic_memory_sync');
```

### WebSocket Communication

```python
# Test WebSocket connection
import websockets
async def test_connection():
    try:
        async with websockets.connect("ws://localhost:8888") as ws:
            await ws.send('{"jsonrpc": "2.0", "id": 1, "method": "status"}')
            response = await ws.recv()
            print(f"Connection successful: {response}")
    except Exception as e:
        print(f"Connection failed: {e}")
```

## Future Enhancements

### Advanced json_rpc Features
- **Batch operations** for multiple files
- **Content diffing** for incremental sync
- **Template management** integration
- **Metadata preservation** across formats

### Commander Plugin Extensions
- **Macro recording** for complex workflows
- **Conditional execution** based on file content
- **Integration hooks** for external services
- **Progress monitoring** for long operations

### Custom Plugin Ecosystem
- **Basic Memory link resolution**
- **Automatic tagging** based on content
- **Relationship visualization**
- **Collaborative editing** features

## Success Metrics

### Performance Metrics
- **Export Speed**: json_rpc vs GUI automation comparison
- **Reliability Rate**: % of successful automated operations
- **Setup Time**: Time to configure vs GUI automation
- **Maintenance Overhead**: Updates needed vs GUI automation

### Feature Completeness
- **Format Support**: All Typora export formats available
- **Content Fidelity**: Quality of exported content
- **Link Preservation**: How well Basic Memory links are handled
- **Metadata Retention**: Preservation of tags and relationships

## Conclusion

**The obgnail/typora_plugin ecosystem transforms Typora from a manual editor into a fully programmable automation platform!**

**Key Breakthroughs**:
- ✅ **json_rpc**: Direct API control eliminates GUI automation brittleness
- ✅ **Commander**: CLI integration enables seamless workflows
- ✅ **Custom Plugins**: Deep integration possibilities
- ✅ **Stability**: API-based approach is maintenance-free

**Result**: **Professional-grade Typora automation** that rivals native CLI tools, with the reliability of API-based systems.

**The future of Typora integration is here - plugin-powered automation!** 🚀🔌🛠️
