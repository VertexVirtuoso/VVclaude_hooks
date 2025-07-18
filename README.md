# VVclaude_hooks

Claude Code hooks system with bidirectional Discord communication.

## Features

- **Notification Hooks**: Get Discord notifications when Claude Code tasks complete
- **Bidirectional Communication**: Send commands to Claude Code via Discord messages
- **Cross-Platform Sound**: System notification sounds (macOS, Windows, Linux)
- **Security**: User ID validation and command sanitization
- **Queue System**: File-based command queue with process management

## Architecture

```
Discord Reply → Discord Bot → Command Queue → Monitor Script → Claude Code
Claude Code → Hook Scripts → Discord Webhook → Discord Notification
```

## Setup

### 1. Install Dependencies

```bash
# Using uv (recommended)
uv install

# Or using pip
pip install requests discord.py
```

### 2. Configure Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to the "Bot" section
4. Create a bot and copy the token
5. Enable "Message Content Intent" in Bot settings
6. Invite the bot to your server with "Send Messages" and "Read Message History" permissions

### 3. Get Your Discord User ID

1. Enable Developer Mode in Discord (User Settings > Advanced > Developer Mode)
2. Right-click your username and select "Copy ID"

### 4. Configure Environment Variables

Update `.env` file with your values:

```env
DISCORD_WEBHOOK=https://discord.com/api/webhooks/YOUR_WEBHOOK_URL
DISCORD_BOT_TOKEN=YOUR_BOT_TOKEN_HERE
AUTHORIZED_USER_ID=YOUR_USER_ID_HERE
```

### 5. Make Scripts Executable

```bash
chmod +x *.py
```

## Usage

### Phase 1: Basic Notifications (✅ Complete)

The notification system is already working! Claude Code will send Discord messages when tasks complete.

### Phase 2: Bidirectional Communication Setup

#### Step 1: Set Up Discord Bot
```bash
# Interactive setup (recommended)
python3 setup_discord_bot.py

# Or check current configuration
python3 validate_bot_config.py
```

#### Step 2: Start Bidirectional Communication
```bash
# Start both Discord bot and command monitor
python3 start_bidirectional.py

# Or start individually
python3 discord_bot.py &
python3 claude_monitor.py &
```

### Send Commands to Claude Code

1. **Reply to webhook notifications**: When you get a Discord notification from Claude Code, reply to it with your command
2. **Direct commands**: Send a message starting with `claude:` or `!claude` or mention the bot
3. **Examples**:
   - Reply to notification: `fix the login bug`
   - Direct command: `claude: add unit tests for the auth module`
   - Mention bot: `@ClaudeBot refactor the database connection`

### Current Hook Configuration

The notification hooks are configured to run automatically when Claude Code tasks complete. Make sure your Claude Code hooks configuration points to the scripts in this directory.

## Security Features

- **User ID Validation**: Only authorized users can send commands
- **Command Sanitization**: Dangerous commands are filtered out
- **Process Limits**: Maximum concurrent Claude Code processes
- **Safe Commands**: Potentially dangerous operations are blocked

## File Structure

```
.
├── discord_bot.py              # Discord bot for listening to commands
├── claude_monitor.py           # Monitor script for executing commands
├── notification.py             # Success notification hook
├── stop.py                     # Stop/failure notification hook
├── start_bidirectional.py      # Startup script for both services
├── .env                        # Environment variables
└── .claude/
    ├── command_queue.json      # Command queue file
    └── processed_commands.json # Processed commands log
```

## Troubleshooting

### Bot Not Responding

1. Check bot token in `.env` file
2. Verify bot has correct permissions in Discord server
3. Check bot logs for authentication errors

### Commands Not Executing

1. Verify Claude Code is installed and in PATH
2. Check monitor script logs
3. Ensure command queue file is readable/writable

### Permission Errors

1. Verify `AUTHORIZED_USER_ID` matches your Discord user ID
2. Check Discord Developer Mode is enabled
3. Ensure you're replying to the correct webhook messages

## Logs

All components log to stdout with timestamps. To save logs:

```bash
python3 start_bidirectional.py > claude_bidirectional.log 2>&1
```
