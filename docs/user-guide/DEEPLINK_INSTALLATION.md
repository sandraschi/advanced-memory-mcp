# One-Click Installation with Deeplinks

Advanced Memory MCP now supports **one-click installation** via deeplinks for Cursor and VS Code!

## 🚀 Quick Install

### For Cursor

#### Option 1: Command Line
```bash
advanced-memory deeplink cursor
```

This generates a deeplink you can click to install instantly in Cursor.

####Option 2: Interactive Setup Wizard
```bash
advanced-memory setup
```

Follow the prompts to configure and install.

### For VS Code

#### Option 1: Command Line
```bash
advanced-memory deeplink vscode
```

#### Option 2: Interactive Setup Wizard
```bash
advanced-memory setup
```

### For Claude Desktop

Claude Desktop doesn't support deeplinks yet, so use:

```bash
advanced-memory deeplink claude-desktop
```

This will show you the configuration to manually add to `claude_desktop_config.json`.

## 📋 All Installation Commands

### Generate Deeplink (stdio - local mode)
```bash
# Cursor - local installation
advanced-memory deeplink cursor

# VS Code - local installation
advanced-memory deeplink vscode

# Claude Desktop - configuration
advanced-memory deeplink claude-desktop
```

### Generate Deeplink (HTTP - network mode)
```bash
# Cursor - network server
advanced-memory deeplink cursor --transport streamable-http --host 127.0.0.1 --port 8000

# VS Code - network server
advanced-memory deeplink vscode --transport streamable-http --host 192.168.1.100 --port 8000
```

### Interactive Setup Wizard
```bash
# Guided setup for any client
advanced-memory setup
```

## 🎯 Transport Modes

### Local Mode (stdio) - Recommended for most users
- **Privacy**: 100% local, no network exposure
- **Speed**: Low latency
- **Use case**: Personal knowledge management
- **Install**: One-click via deeplink

```bash
advanced-memory deeplink cursor  # Local by default
```

### Network Mode (streamable-http) - For teams & cloud
- **Access**: Available via HTTP/HTTPS
- **Use case**: Team collaboration, cloud deployment
- **Requires**: Running server instance

```bash
# Generate deeplink
advanced-memory deeplink cursor --transport streamable-http --port 8000

# Start server (separate terminal)
advanced-memory mcp --transport streamable-http --port 8000
```

## 🔧 Examples

### Example 1: Local Cursor Install
```bash
$ advanced-memory deeplink cursor

┌─────────────── 🎯 Cursor Deeplink ────────────────┐
│ cursor://anysphere.cursor-deeplink/mcp/install... │
└───────────────── Click to install ────────────────┘

✨ Click the link above to install in Cursor!
```

### Example 2: Network VS Code Install
```bash
$ advanced-memory deeplink vscode --transport streamable-http --host 192.168.1.50 --port 9000

┌─────────────── 📝 VS Code Deeplink ───────────────┐
│ vscode:mcp/install?%7B%22name%22%3A%22advanced... │
└───────────────── Click to install ────────────────┘

✨ Click the link above to install in VS Code!
This will connect to Advanced Memory MCP at streamable-http://192.168.1.50:9000/mcp
```

### Example 3: Interactive Setup
```bash
$ advanced-memory setup

🚀 Advanced Memory MCP Setup Wizard

Which AI client are you using?

  1. Cursor IDE
  2. VS Code (with ChatGPT/Claude extensions)
  3. Claude Desktop
  4. Other/Manual setup

Enter number [1]: 1

How do you want to run Advanced Memory?

  1. Local (stdio) - Runs on your machine [recommended]
  2. Network (HTTP) - Accessible via network

Enter number [1]: 1

✓ Using local mode (maximum privacy)

✨ Configuration Generated!

┌─────────────── 🎯 Cursor Installation Link ───────────────┐
│ cursor://anysphere.cursor-deeplink/mcp/install?name=adv...│
└────────────────────────────────────────────────────────────┘

Open installation link in browser? [Y/n]: y
✓ Opening link in browser...

→ Cursor should prompt you to install Advanced Memory MCP
→ Click 'Install' to complete setup

Next Steps:
  1. Install will happen automatically via the link
  2. Start using Advanced Memory MCP in your AI client!
  3. Try: 'Create a note about Python best practices'

✨ Setup complete! Happy note-taking!
```

## 🔐 Security Notes

### Local Mode (stdio)
- ✅ Maximum security - no network exposure
- ✅ Filesystem permissions only
- ✅ No authentication needed
- ✅ Recommended for personal use

### Network Mode (streamable-http)
- ⚠️ Exposed to network
- ⚠️ Consider authentication (future feature)
- ⚠️ Use firewall rules for protection
- ⚠️ HTTPS recommended for production

**Recommendation**: Use local mode (stdio) unless you specifically need team/cloud access.

## 📚 Related Documentation

- [CLI Command Reference](cli-command-reference.md) - All CLI commands
- [Deployment Options](../operations/deployment-options.md) - Detailed transport comparison
- [Triple-Interface Guide](triple-interface.md) - Understanding stdio, HTTP, and SSE modes
- [Troubleshooting](../TROUBLESHOOTING_GUIDE.md) - Common issues and solutions

## ❓ FAQ

### Q: What's a deeplink?
A: A deeplink is a special URL that your AI client recognizes and uses to automatically configure the MCP server. It's like a one-click installer!

### Q: Do deeplinks work offline?
A: Yes! For stdio (local) mode, the deeplink just configures your client to run Advanced Memory locally.

### Q: Can I use both local and network modes?
A: Not simultaneously from the same command, but you can generate separate deeplinks for each mode and use them as needed.

### Q: Why doesn't Claude Desktop support deeplinks?
A: Claude Desktop requires manual configuration file editing. We provide the exact JSON you need to add.

### Q: Are deeplinks secure?
A: Yes! Deeplinks are just configuration URLs. For stdio mode, they simply tell your client how to run the local process. No credentials or sensitive data.

## 🐛 Troubleshooting

### Deeplink doesn't open
- Try copying the link and pasting it into your browser's address bar
- Make sure your AI client (Cursor/VS Code) is installed and up to date

### "Server not found" error after installation
- **For stdio mode**: No additional steps needed, it runs automatically
- **For HTTP mode**: Make sure you've started the server with `advanced-memory mcp --transport streamable-http`

### VS Code doesn't recognize the deeplink
- Ensure VS Code is updated to the latest version
- Try the manual installation method from the [main documentation](../README.md)

---

**Made installation too easy?** We think so! 🎉

**Need help?** Check our [Troubleshooting Guide](../TROUBLESHOOTING_GUIDE.md) or open an issue on GitHub.


