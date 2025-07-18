# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Claude Code hooks system that provides Discord notifications and bidirectional communication with Claude Code. The system includes:

- **Notification Hooks**: Send Discord notifications when Claude Code tasks complete
- **Bidirectional Communication**: Send commands to Claude Code via Discord messages
- **Command Queue System**: File-based queue for managing remote commands
- **Security Features**: User authentication and command sanitization

## Architecture

### Core Components

**Notification System (One-way: Claude Code → Discord)**
- **notification.py**: Hook script that executes on task completion
- **stop.py**: Identical to notification.py (may be used for different hook events)

**Bidirectional Communication System (Two-way: Discord ↔ Claude Code)**
- **discord_bot.py**: Discord bot that listens for command messages
- **claude_monitor.py**: Monitor script that executes queued commands
- **start_bidirectional.py**: Startup script for both services
- **command_queue.json**: File-based command queue
- **processed_commands.json**: Log of processed commands

**Configuration**
- **.env**: Contains Discord webhook URL, bot token, and authorized user ID
- **.claude/settings.local.json**: Claude Code permissions configuration

### Execution Flows

**Notification Flow (Claude Code → Discord)**
1. Claude Code triggers hook with JSON input containing session information
2. Script plays system notification sound (cross-platform compatible)
3. Script sends Discord message via webhook
4. Script exits with success status

**Command Flow (Discord → Claude Code)**
1. User replies to Discord notification or sends direct command
2. Discord bot validates user and sanitizes command
3. Command is queued in command_queue.json
4. Monitor script detects new command and executes via `claude-code -p`
5. Claude Code processes command and triggers notification hooks
6. Completion notification sent back to Discord

### Cross-Platform Sound Support

The scripts implement cascading fallback for Linux sound systems:
- `paplay` (PulseAudio)
- `aplay` (ALSA) 
- `speaker-test` (generates test tones)
- `beep` (system beep)
- Terminal bell as final fallback

## Environment Configuration

### Required Environment Variables

- `DISCORD_WEBHOOK`: Discord webhook URL for notifications (loaded from .env file)

### .env File Location Priority

Scripts search for .env files in this order:
1. `~/.claude/hooks/.env`
2. `/home/charlie/.claude/hooks/.env`
3. Current working directory

## Common Development Tasks

### Testing Hook Scripts

To test notification.py manually:
```bash
echo '{"session_id": "test-session"}' | python3 notification.py
```

### Testing Bidirectional Communication

1. **Start the system**:
```bash
python3 start_bidirectional.py
```

2. **Send test command** (in Discord):
   - Reply to a webhook notification: `help me fix this bug`
   - Direct command: `claude: explain the codebase structure`

3. **Monitor logs** for command processing

### Making Scripts Executable

```bash
chmod +x *.py
```

### Installing Dependencies

```bash
# Using uv (recommended)
uv install

# Or using pip
pip install requests discord.py
```

## Security Considerations

- **Environment Variables**: Discord webhook URL and bot token in .env file should not be committed to git
- **User Authentication**: Only authorized user ID can send commands via Discord
- **Command Sanitization**: Dangerous commands are filtered out before execution
- **Process Limits**: Maximum concurrent Claude Code processes to prevent resource exhaustion
- **Sound Commands**: System commands for notifications are predefined and safe
- **Claude Code Permissions**: Configured in .claude/settings.local.json

## Integration Points

### Discord Integration
- **Webhook-based notifications**: Send completion messages to Discord
- **Bot-based commands**: Listen for and process user commands
- **User authentication**: Validate commands from authorized users only
- **Message includes**: Session ID, completion status, and command details
- **Graceful fallback**: When webhook/bot is unavailable

### Claude Code Integration
- **Notification hooks**: Hooks into Claude Code's lifecycle events
- **Command execution**: Executes commands via `claude-code -p` non-interactive mode
- **JSON input**: Receives session metadata via stdin
- **Queue system**: File-based command queue for remote execution
- **Process management**: Monitors and limits concurrent Claude Code instances
- **Exit codes**: Must exit with status 0 for successful completion

## File Structure

```
/home/charlie/.claude/hooks/
├── notification.py          # Primary notification hook script
├── stop.py                  # Duplicate of notification.py
├── discord_bot.py           # Discord bot for command listening
├── claude_monitor.py        # Command queue monitor and executor
├── start_bidirectional.py   # Startup script for bidirectional system
├── .env                     # Environment variables (webhook, bot token, user ID)
├── pyproject.toml           # Python project dependencies
└── .claude/
    ├── settings.local.json  # Claude Code permissions
    ├── command_queue.json   # Command queue file
    └── processed_commands.json  # Processed commands log
```