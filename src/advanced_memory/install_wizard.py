"""
Basic Memory Installation Wizard

This module provides an interactive setup for configuring Basic Memory
with various IDEs and tools.
"""

import os
import sys
import json
import shutil
from pathlib import Path
import platform

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    """Display the ASCII banner."""
    banner = r"""
     ____        _      _____                          
    |  _ \      | |    |  __ \                         
    | |_) | __ _| | __ | |__) |_ _ _ __   __ _ ___ ___ 
    |  _ < / _` | |/ / |  ___/ _` | '_ \ / _` / __/ __|
    | |_) | (_| |   <  | |  | (_| | | | | (_| \__ \__ \
    |____/ \__,_|_|\_\ |_|   \__,_|_| |_|\__,_|___/___/
    
    Advanced Memory - Installation Wizard
    ====================================
    """
    print(banner)

def get_config_path(app_name):
    """Get the configuration file path for the given application."""
    system = platform.system()
    if system == "Windows":
        return Path(os.environ['APPDATA']) / app_name / 'config.json'
    elif system == "Darwin":  # macOS
        return Path.home() / 'Library' / 'Application Support' / app_name / 'config.json'
    else:  # Linux and others
        return Path.home() / '.config' / app_name / 'config.json'

def backup_file(file_path):
    """Create a backup of the file if it exists."""
    if not file_path.exists():
        return file_path
    backup_path = file_path.with_name(f"{file_path.name}.bak")
    shutil.copy2(file_path, backup_path)
    return backup_path

def configure_windsurf():
    """Configure Windsurf to use Basic Memory as an MCP client."""
    config_path = get_config_path('windsurf')
    backup_path = backup_file(config_path)
    
    # Create or update config
    config = {}
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            try:
                config = json.load(f)
            except json.JSONDecodeError:
                config = {}
    
    # Update MCP settings
    if 'mcp' not in config:
        config['mcp'] = {}
    if 'clients' not in config['mcp']:
        config['mcp']['clients'] = {}
    
    config['mcp']['clients']['basic-memory'] = {
        'enabled': True,
        'transport': 'stdio',
        'command': os.path.abspath(sys.executable),
        'args': ['mcp', '--transport', 'stdio'],
        'cwd': str(Path.home() / 'Documents' / 'Notes')
    }
    
    # Save config
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    
    return config_path, backup_path

def show_help():
    """Display the help information."""
    help_text = """
    ===== Basic Memory - Quick Start Guide =====
    
    Basic Memory is now installed and running as an MCP server.
    
    Key Features:
    - Store and retrieve notes with rich markdown support
    - Full-text search across all your notes
    - Tag and categorize your knowledge
    
    Quick Commands:
    - Start the MCP server: basic-memory mcp
    - List all notes: basic-memory list
    - Create a note: basic-memory new "Note Title"
    
    For more help, visit:
    https://github.com/sandraschi/basic-memory
    
    Press Enter to exit...
    """
    input(help_text)

def main():
    """Main entry point for the installation wizard."""
    clear_screen()
    print_banner()
    
    print("1. Set up Claude integration")
    print("2. Set up Windsurf integration")
    print("3. Set up Cursor IDE integration")
    print("4. Exit")
    
    choice = input("\nSelect an option (1-4): ").strip()
    
    if choice == '1':
        print("\nClaude integration is automatic when using Claude Desktop.")
    elif choice == '2':
        try:
            config_path, backup_path = configure_windsurf()
            print(f"\n✓ Windsurf configuration updated!")
            print(f"  Config file: {config_path}")
            if backup_path != config_path:
                print(f"  Backup saved to: {backup_path}")
        except Exception as e:
            print(f"\nError configuring Windsurf: {e}")
    elif choice == '3':
        print("\nCursor IDE integration coming soon!")
    else:
        print("\nInstallation cancelled.")
        return
    
    input("\nPress Enter to show help...")
    show_help()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInstallation cancelled by user.")
        sys.exit(1)
