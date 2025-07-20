# Bidirectional Communication Setup Guide

## Current Status ✅

Your bidirectional communication system is **successfully implemented** with these components:

### ✅ Working Components:
1. **Discord Bot** - ✅ Connected and ready to receive commands
2. **Webhook Notifications** - ✅ Working with task-specific sounds  
3. **Command Queue System** - ✅ Implemented and ready
4. **Command Monitor** - ✅ Implemented, needs Claude Code path

### 🔧 Configuration Needed:

**Claude Code Path**: The monitor script needs the correct path to your Claude Code executable.

## Quick Setup

### 1. Find Your Claude Code Installation

Run one of these commands to find Claude Code:
```bash
# Check if it's available as 'claude'
which claude

# Check if it's installed via npm/yarn globally
which claude-cli

# Check in common installation directories
ls -la ~/.local/bin/ | grep claude
ls -la /usr/local/bin/ | grep claude
```

### 2. Update Monitor Configuration

Edit `/home/charlie/.claude/hooks/claude_monitor.py` and update line 26:
```python
# Current:
CLAUDE_CODE_COMMAND = "claude-code"

# Update to your actual command, for example:
CLAUDE_CODE_COMMAND = "claude"
# OR
CLAUDE_CODE_COMMAND = "/path/to/claude-code"
```

### 3. Test the System

Once configured, start the system:
```bash
cd /home/charlie/.claude/hooks
uv run python3 start_bidirectional.py
```

## How It Works

### 📤 Commands FROM Discord TO Claude Code:
1. **Reply to webhook messages**: Reply to any Claude Code completion notification
2. **Direct commands**: Send `claude: <your command>` in Discord
3. **Bot mentions**: Mention the bot with `@Claude_messanger <command>`

### 📥 Notifications FROM Claude Code TO Discord:
- **Automatic**: Every Claude Code task completion sends notification
- **Sound-aware**: Different sounds for research/implementation/testing
- **Rich info**: Includes system context, git status, project info

### 🔒 Security Features:
- **User authentication**: Only your Discord user ID can send commands
- **Command sanitization**: Dangerous commands are filtered
- **Process limits**: Max 1 concurrent Claude Code instance

## Current Configuration

Your `.env` file is properly configured with:
- ✅ Discord webhook URL (working)
- ✅ Discord bot token (working) 
- ✅ Authorized user ID (set to your Discord ID)

## Testing Commands

Once the Claude Code path is configured, try these Discord commands:

1. **Reply to a notification**: "help me understand this code"
2. **Direct command**: "claude: explain the project structure"
3. **Bot mention**: "@Claude_messanger show me the git status"

## Next Steps

1. **Find Claude Code path** and update `claude_monitor.py`
2. **Start the system** with `start_bidirectional.py`
3. **Test commands** from Discord
4. **Add custom sounds** for different task types (optional)

The system is ready - it just needs the correct Claude Code command path!