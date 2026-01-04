# PowerShell Debugging in Cursor/VS Code

**Guide**: How to debug PowerShell scripts with breakpoints in Cursor editor
**Date**: 2025-12-02

---

## ✅ Yes, You Can Debug PowerShell Scripts!

Cursor (based on VS Code) supports full PowerShell debugging with:
- ✅ **Breakpoints** - Click in the gutter or press `F9`
- ✅ **Step through code** - F10 (step over), F11 (step into), Shift+F11 (step out)
- ✅ **Variable inspection** - Hover over variables or use Variables panel
- ✅ **Watch expressions** - Monitor specific variables/expressions
- ✅ **Call stack** - See execution path
- ✅ **Debug console** - Execute PowerShell commands during debugging

---

## Prerequisites

### 1. Install PowerShell Extension

1. Open Cursor/VS Code
2. Go to Extensions (`Ctrl+Shift+X`)
3. Search for **"PowerShell"**
4. Install **"PowerShell"** by Microsoft (ms-vscode.PowerShell)

### 2. Verify Installation

- PowerShell extension icon should appear in the sidebar
- You should see PowerShell version in status bar (bottom right)
- PowerShell commands available in Command Palette (`Ctrl+Shift+P`)

---

## Setting Up Debug Configuration

### Automatic Setup

A `.vscode/launch.json` file has been created with debug configurations for the backup script.

### Manual Setup

1. Open Command Palette (`Ctrl+Shift+P`)
2. Type: `Debug: Add Configuration`
3. Select: `PowerShell`
4. Choose configuration type

---

## Using Debugger

### Setting Breakpoints

**Method 1: Click in Gutter**
- Click to the left of line numbers (red dot appears)
- Click again to remove

**Method 2: Keyboard**
- Place cursor on line
- Press `F9` to toggle breakpoint

**Method 3: Conditional Breakpoints**
- Right-click in gutter
- Select "Add Conditional Breakpoint"
- Enter condition (e.g., `$ErrorCount -gt 0`)

### Starting Debug Session

**Method 1: Using Launch Configuration**
1. Open `scripts/backup-repo.ps1`
2. Press `F5` or click Debug button
3. Select configuration from dropdown:
   - "PowerShell: Debug Backup Script"
   - "PowerShell: Debug Backup Script (WhatIf)"
   - "PowerShell: Debug Backup Script (IncludeBuild)"

**Method 2: Quick Debug**
1. Open any `.ps1` file
2. Press `F5`
3. Select "PowerShell: Debug Current Script"

### Debug Controls

| Key | Action |
|-----|--------|
| `F5` | Start/Continue debugging |
| `F9` | Toggle breakpoint |
| `F10` | Step Over (execute line, don't enter functions) |
| `F11` | Step Into (enter functions) |
| `Shift+F11` | Step Out (exit current function) |
| `Shift+F5` | Stop debugging |
| `Ctrl+Shift+F5` | Restart debugging |

### Run to Cursor

1. Place cursor on desired line
2. Right-click → "Run to Cursor" or `Ctrl+F10`
3. Script runs and stops at cursor position

---

## Debugging Features

### Variables Panel

**Location**: Left sidebar during debug session

**Shows**:
- **Local** - Variables in current scope
- **Globals** - Global variables
- **Script** - Script-scoped variables (like `$script:ErrorCount`)

**Actions**:
- Expand objects to see properties
- Hover over variables to see values
- Right-click → "Set Value" to modify variables

### Watch Panel

**Add Watch Expression**:
1. Click "+" in Watch panel
2. Enter variable name or expression
3. Press Enter

**Examples**:
- `$backupFiles.Count`
- `$ErrorCount`
- `$script:LogFile`

### Call Stack

**Location**: Left sidebar during debug session

**Shows**:
- Current execution path
- Function call hierarchy
- Click to navigate to different stack frames

### Debug Console

**Location**: Bottom panel during debug session

**Use for**:
- Execute PowerShell commands
- Inspect variables: `$variableName`
- Evaluate expressions: `$backupFiles.Count`
- Modify variables: `$ErrorCount = 5`

**Examples**:
```powershell
# Check variable value
$ErrorCount

# Inspect object
$backupFiles[0] | Format-List

# Check path
Test-Path $backupPath1

# Modify variable (for testing)
$script:ErrorCount = 0
```

---

## Debugging the Backup Script

### Step-by-Step Debugging

1. **Open script**: `scripts/backup-repo.ps1`

2. **Set breakpoints**:
   - Line 75: `function Write-Log` (start of logging)
   - Line 295: `Write-Log "Scanning repository files..."` (file scanning)
   - Line 581: `Write-Log "Creating Desktop backup..."` (backup creation)
   - Line 634: `New-BackupZip` call (ZIP creation)

3. **Start debugging**:
   - Press `F5`
   - Select "PowerShell: Debug Backup Script (WhatIf)" for safe testing

4. **Debug session starts**:
   - Script pauses at first breakpoint
   - Use F10/F11 to step through
   - Inspect variables in Variables panel

### Useful Breakpoints

**Error Handling**:
- Line 143: `function Write-ErrorDetails` - Catch errors
- Line 164: `function Exit-WithError` - See error exits

**File Operations**:
- Line 295: File scanning start
- Line 350: File filtering logic
- Line 634: ZIP creation start

**Backup Creation**:
- Line 581: Desktop backup start
- Line 618: N: Drive backup start
- Line 655: OneDrive backup start

### Testing Error Scenarios

**Simulate Errors**:

1. **Set breakpoint** at error handling code
2. **In Debug Console**, set:
   ```powershell
   $script:ErrorCount = 1
   ```
3. **Continue execution** to see error handling in action

**Test Missing Files**:
1. Set breakpoint in `New-BackupZip`
2. In Debug Console:
   ```powershell
   $Files = @()  # Empty array to test error handling
   ```

---

## Debugging Tips

### 1. Conditional Breakpoints

Set breakpoints that only trigger under specific conditions:

**Example**: Break only when errors occur
```
$script:ErrorCount -gt 0
```

**Example**: Break when processing specific file
```
$file.Name -eq "backup-repo.ps1"
```

**Example**: Break in loop after N iterations
```
$fileCount -gt 100
```

### 2. Logpoints

**Logpoints** output to console without modifying code:

1. Right-click in gutter
2. Select "Add Logpoint"
3. Enter message: `File: ${file.Name}, Count: ${fileCount}`

### 3. Exception Breakpoints

Break automatically when exceptions occur:

1. Open Breakpoints panel (left sidebar)
2. Check "All Exceptions" or "Uncaught Exceptions"
3. Script pauses when exceptions are thrown

### 4. Debug Output

View debug output:
- **Debug Console** - Shows Write-Host output
- **Output Panel** - Select "PowerShell" from dropdown

---

## Troubleshooting

### PowerShell Extension Not Working

**Symptoms**:
- No breakpoints hit
- PowerShell commands not available
- No PowerShell in status bar

**Solutions**:
1. **Reload window**: `Ctrl+Shift+P` → "Developer: Reload Window"
2. **Check extension**: Verify PowerShell extension is installed and enabled
3. **Check PowerShell version**: Ensure PowerShell 5.1+ or PowerShell 7+
4. **Restart Cursor**: Close and reopen Cursor

### Breakpoints Not Hitting

**Common Causes**:
- Script path incorrect
- Script not executing (error before breakpoint)
- PowerShell extension not loaded
- Wrong debug configuration selected

**Solutions**:
1. Verify script path in launch.json
2. Check Debug Console for errors
3. Try adding `Write-Host "Debug point"` to verify execution
4. Check Output panel for PowerShell messages

### Variables Not Showing

**Solutions**:
1. Ensure you're paused at breakpoint (not just running)
2. Check variable scope (Local vs Global vs Script)
3. Expand object properties in Variables panel
4. Use Debug Console to inspect: `$variableName`

### Script Execution Errors

**Common Issues**:
- Execution policy blocking script
- Missing modules or dependencies
- Path issues

**Solutions**:
1. Check execution policy:
   ```powershell
   Get-ExecutionPolicy
   Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
   ```

2. Check script path in launch.json:
   ```json
   "script": "${workspaceFolder}/scripts/backup-repo.ps1",
   "cwd": "${workspaceFolder}"
   ```

3. Check Debug Console for detailed error messages

---

## Advanced Debugging

### Remote Debugging

Attach to running PowerShell process:

1. Use configuration: "PowerShell: Attach to Process"
2. Enter process ID or select from list
3. Set breakpoints before attaching

### Multi-File Debugging

Debug scripts that call other scripts:

1. Set breakpoints in all relevant files
2. Use "Step Into" (F11) to enter called functions
3. Use "Step Out" (Shift+F11) to return

### Debugging Modules

Debug PowerShell modules:

1. Import module in script
2. Set breakpoints in module file
3. Start debugging main script
4. Breakpoints in module will work

---

## Launch Configurations Available

### 1. Debug Backup Script
- Runs with `-Verbose` flag
- Full backup execution
- Best for normal debugging

### 2. Debug Backup Script (WhatIf)
- Runs with `-WhatIf` flag
- Safe - no files created
- Best for testing logic

### 3. Debug Backup Script (IncludeBuild)
- Includes build artifacts
- Tests with more files
- Best for testing exclusions

### 4. Debug Backup Script (List)
- Shows backup history
- No backup creation
- Best for testing list feature

### 5. Debug Current Script
- Debugs any open `.ps1` file
- Flexible for any script
- Best for quick debugging

---

## Quick Reference

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `F5` | Start/Continue |
| `F9` | Toggle breakpoint |
| `F10` | Step Over |
| `F11` | Step Into |
| `Shift+F11` | Step Out |
| `Shift+F5` | Stop |
| `Ctrl+Shift+F5` | Restart |
| `Ctrl+F10` | Run to Cursor |

### Debug Panel Sections

- **Variables**: Current variable values
- **Watch**: Monitored expressions
- **Call Stack**: Execution path
- **Breakpoints**: All breakpoints
- **Debug Console**: PowerShell REPL

---

## Example Debug Session

### Scenario: Debug File Scanning

1. **Set breakpoint** at line 295: `Write-Log "Scanning repository files..."`
2. **Press F5** → Select "PowerShell: Debug Backup Script (WhatIf)"
3. **Script pauses** at breakpoint
4. **Step through** (F10):
   - Line 297: Get repository root
   - Line 301: Scan all files
   - Line 315: Apply exclusions
5. **Inspect variables**:
   - `$allFiles.Count` - Total files found
   - `$backupFiles.Count` - Files after filtering
   - `$backupSize` - Size calculation
6. **Continue** (F5) or step through to next breakpoint

---

## Related Files

- Debug configuration: `.vscode/launch.json`
- Backup script: `scripts/backup-repo.ps1`
- This guide: `docs/POWERSHELL_DEBUGGING_GUIDE.md`

---

## Tags
#powershell #debugging #cursor #vscode #breakpoints #development #tooling

---

**Last Updated**: 2025-12-02
