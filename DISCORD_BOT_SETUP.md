# Discord Bot Setup Guide

This guide will walk you through setting up a Discord bot for bidirectional communication with Claude Code.

## Prerequisites

- Discord account
- Server admin permissions (to add the bot)
- Access to Discord Developer Portal

## Step 1: Create Discord Application

1. **Go to Discord Developer Portal**
   - Visit: https://discord.com/developers/applications
   - Click "New Application"
   - Name your application (e.g., "Claude Code Bot")
   - Click "Create"

2. **Configure Application**
   - Add description: "Bot for bidirectional communication with Claude Code"
   - Add icon (optional)
   - Save changes

## Step 2: Create Bot User

1. **Go to Bot Section**
   - Click "Bot" in the left sidebar
   - Click "Add Bot"
   - Confirm "Yes, do it!"

2. **Configure Bot Settings**
   - **Username**: Change to "Claude Code Bot" (or your preference)
   - **Bot Icon**: Upload an icon (optional)
   - **Public Bot**: Turn OFF (keep private)
   - **Require OAuth2 Code Grant**: Turn OFF

3. **Important Bot Settings**
   - **Message Content Intent**: Turn ON (required for reading messages)
   - **Server Members Intent**: Turn OFF (not needed)
   - **Presence Intent**: Turn OFF (not needed)

## Step 3: Get Bot Token

1. **Copy Bot Token**
   - In the Bot section, click "Copy" under "Token"
   - **⚠️ IMPORTANT**: Never share this token publicly!
   - Save it for Step 5

## Step 4: Set Bot Permissions

1. **Go to OAuth2 > URL Generator**
   - **Scopes**: Check "bot"
   - **Bot Permissions**: Check the following:
     - ✅ Read Messages/View Channels
     - ✅ Send Messages
     - ✅ Read Message History
     - ✅ Add Reactions
     - ✅ Use Slash Commands (optional)

2. **Generate Invite URL**
   - Copy the generated URL at the bottom
   - Save it for Step 6

## Step 5: Configure Environment Variables

1. **Get Your Discord User ID**
   - In Discord, go to User Settings > Advanced
   - Turn ON "Developer Mode"
   - Right-click your username anywhere
   - Click "Copy ID"

2. **Update .env File**
   ```bash
   # Update /home/charlie/.claude/hooks/.env
   nano .env
   ```
   
   Add your bot token and user ID:
   ```env
   # Replace YOUR_BOT_TOKEN_HERE with the token from Step 3
   DISCORD_BOT_TOKEN=YOUR_BOT_TOKEN_HERE
   
   # Replace YOUR_USER_ID_HERE with your Discord user ID
   AUTHORIZED_USER_ID=YOUR_USER_ID_HERE
   ```

## Step 6: Add Bot to Your Server

1. **Use the Invite URL**
   - Use the URL generated in Step 4
   - Select your Discord server
   - Click "Authorize"
   - Complete the captcha

2. **Verify Bot is in Server**
   - Check your server's member list
   - The bot should appear as offline (this is normal)

## Step 7: Test Bot Configuration

1. **Test Bot Token**
   ```bash
   cd /home/charlie/.claude/hooks
   python3 -c "
   import os
   from pathlib import Path
   
   # Load .env file
   env_path = Path('.env')
   if env_path.exists():
       with open(env_path, 'r') as f:
           for line in f:
               if line.startswith('DISCORD_BOT_TOKEN='):
                   token = line.split('=', 1)[1].strip()
                   if token and token != 'YOUR_BOT_TOKEN_HERE':
                       print('✅ Bot token found and configured')
                   else:
                       print('❌ Bot token not configured')
                   break
   else:
       print('❌ .env file not found')
   "
   ```

2. **Test Bot Connection**
   ```bash
   cd /home/charlie/.claude/hooks
   uv run python3 discord_bot.py
   ```
   
   You should see:
   ```
   Discord bot logged in as Claude Code Bot (ID: xxxxxxxxxx)
   Authorized user ID: your_user_id
   ```

## Step 8: Test Bidirectional Communication

1. **Start the Full System**
   ```bash
   cd /home/charlie/.claude/hooks
   python3 start_bidirectional.py
   ```

2. **Test Commands**
   - In Discord, send a message: `claude: help me understand this project`
   - The bot should react with ✅ and reply with confirmation
   - Check the monitor logs for command processing

## Troubleshooting

### Bot Not Responding
- Check bot token is correct
- Verify bot has "Message Content Intent" enabled
- Make sure bot has proper permissions in your server

### "Unauthorized" Error
- Bot token is invalid or expired
- Regenerate token in Discord Developer Portal

### "Permission Denied" Error
- Bot lacks necessary permissions
- Re-invite bot with correct permissions

### Bot Can't Read Messages
- "Message Content Intent" is disabled
- Enable it in Discord Developer Portal > Bot

## Security Notes

- ✅ Bot token is in .env file (ignored by git)
- ✅ Only authorized user can send commands
- ✅ Commands are sanitized before execution
- ✅ Rate limiting and error handling in place

## Next Steps

Once your bot is working:
1. Test the notification system (Phase 1)
2. Test bidirectional commands (Phase 2)
3. Move to Phase 3 for advanced features

---

**Need Help?**
- Discord Developer Documentation: https://discord.com/developers/docs
- Discord.py Documentation: https://discordpy.readthedocs.io/