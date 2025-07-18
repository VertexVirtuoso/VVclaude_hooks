# Phase 2.1: Discord Bot Setup

You're ready to set up bidirectional communication! This will allow you to send commands to Claude Code via Discord messages.

## Quick Start

### Option 1: Interactive Setup (Recommended)
```bash
cd /home/charlie/.claude/hooks
python3 setup_discord_bot.py
```

### Option 2: Manual Setup
1. Follow the detailed guide: `cat DISCORD_BOT_SETUP.md`
2. Update your `.env` file with bot token and user ID
3. Validate configuration: `python3 validate_bot_config.py`

## What You Need

### 1. Discord Bot Token
- Go to https://discord.com/developers/applications
- Create a new application
- Create a bot user
- Copy the bot token

### 2. Your Discord User ID
- Enable Developer Mode in Discord settings
- Right-click your username → Copy ID

### 3. Bot Permissions
- Read Messages/View Channels
- Send Messages  
- Read Message History
- Add Reactions
- Message Content Intent (Important!)

## Current Status

```bash
# Check what's configured
python3 validate_bot_config.py
```

Expected output after setup:
```
✅ discord.py library is available
✅ Bot token format looks valid
✅ User ID format looks valid
✅ Discord webhook URL is configured
🎉 Configuration looks good! Ready to start the bot.
```

## Testing

### 1. Test Bot Connection
```bash
python3 discord_bot.py
```

Should show:
```
Discord bot logged in as YourBot (ID: xxxxxxxxxx)
Authorized user ID: your_user_id
```

### 2. Test Full System
```bash
python3 start_bidirectional.py
```

### 3. Send Test Command
In Discord, send: `claude: help me understand this project`

## Files Created

- `DISCORD_BOT_SETUP.md` - Detailed setup guide
- `validate_bot_config.py` - Configuration validator
- `setup_discord_bot.py` - Interactive setup script
- `PHASE2_README.md` - This file
- Updated `.gitignore` - Protects sensitive files

## Security

✅ Bot token stored in `.env` (git-ignored)
✅ Only authorized user can send commands
✅ Commands are sanitized before execution
✅ Rate limiting and error handling

## Troubleshooting

### "discord.py library not found"
```bash
uv sync
```

### "Bot token not configured"
```bash
python3 setup_discord_bot.py
```

### "Bot not responding"
- Check bot has "Message Content Intent" enabled
- Verify bot is in your Discord server
- Check bot permissions

## Next Steps

Once Phase 2.1 is complete:
- ✅ Bot connects to Discord
- ✅ Bot receives your commands
- ✅ Commands are queued for execution
- ✅ Claude Code processes commands
- ✅ Results sent back to Discord

Ready for Phase 2.2: Bot Testing & Validation!