#!/usr/bin/env python3
"""
Discord bot for bidirectional communication with Claude Code.
Listens for replies to webhook messages and queues commands for execution.
"""

import os
import discord
import json
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
def load_env_vars():
    """Load environment variables from .env file"""
    env_paths = [
        Path.home() / ".claude" / "hooks" / ".env",
        Path("/home/charlie/.claude/hooks/.env"),
        Path.cwd() / ".env"
    ]
    
    env_vars = {}
    for env_path in env_paths:
        if env_path.exists():
            try:
                with open(env_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if '=' in line and not line.startswith('#'):
                            key, value = line.split('=', 1)
                            env_vars[key] = value
            except Exception as e:
                logger.error(f"Error reading {env_path}: {e}")
    
    return env_vars

# Load configuration
env_vars = load_env_vars()
DISCORD_BOT_TOKEN = env_vars.get('DISCORD_BOT_TOKEN') or os.getenv('DISCORD_BOT_TOKEN')
AUTHORIZED_USER_ID = env_vars.get('AUTHORIZED_USER_ID') or os.getenv('AUTHORIZED_USER_ID')
COMMAND_QUEUE_FILE = Path.home() / ".claude" / "command_queue.json"
WEBHOOK_BOT_NAME = "Claude Code Hooks"  # Name that appears in webhook messages

# Ensure command queue directory exists
COMMAND_QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)

class ClaudeCommandBot(discord.Client):
    def __init__(self, *args, **kwargs):
        # Enable necessary intents
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents, *args, **kwargs)
        
        self.authorized_user_id = None
        if AUTHORIZED_USER_ID:
            try:
                self.authorized_user_id = int(AUTHORIZED_USER_ID)
            except ValueError:
                logger.error(f"Invalid AUTHORIZED_USER_ID: {AUTHORIZED_USER_ID}")

    async def on_ready(self):
        """Called when bot is ready"""
        logger.info(f'Discord bot logged in as {self.user} (ID: {self.user.id})')
        if self.authorized_user_id:
            logger.info(f'Authorized user ID: {self.authorized_user_id}')
        else:
            logger.warning('No authorized user ID configured - bot will respond to all users')

    async def on_message(self, message):
        """Handle incoming messages"""
        # Ignore messages from bots (including self)
        if message.author.bot:
            return
            
        # Check if user is authorized
        if self.authorized_user_id and message.author.id != self.authorized_user_id:
            logger.info(f'Ignoring message from unauthorized user: {message.author.id}')
            return
            
        # Check if message is a reply to a webhook message
        if message.reference and message.reference.message_id:
            try:
                # Get the original message
                original_message = await message.channel.fetch_message(message.reference.message_id)
                
                # Check if it's from our webhook (by author name)
                if (original_message.author.name == WEBHOOK_BOT_NAME or 
                    original_message.webhook_id is not None):
                    
                    # Extract command from the reply
                    command_text = message.content.strip()
                    
                    if command_text:
                        await self.queue_command(command_text, message)
                    else:
                        await message.add_reaction('❓')
                        
            except discord.NotFound:
                logger.warning(f'Could not find original message {message.reference.message_id}')
            except discord.Forbidden:
                logger.warning('Bot lacks permission to fetch message')
            except Exception as e:
                logger.error(f'Error handling reply: {e}')
                
        # Handle direct commands (messages starting with claude: or @bot)
        elif (message.content.startswith('claude:') or 
              message.content.startswith('!claude') or
              self.user in message.mentions):
            
            # Extract command text
            command_text = message.content
            for prefix in ['claude:', '!claude', f'<@{self.user.id}>']:
                if command_text.startswith(prefix):
                    command_text = command_text[len(prefix):].strip()
                    break
                    
            if command_text:
                await self.queue_command(command_text, message)
            else:
                await message.add_reaction('❓')

    async def queue_command(self, command_text: str, message: discord.Message):
        """Queue a command for execution"""
        try:
            # Sanitize command
            sanitized_command = self.sanitize_command(command_text)
            
            # Create command entry
            command_entry = {
                "timestamp": datetime.now().isoformat(),
                "command": sanitized_command,
                "original_command": command_text,
                "user_id": message.author.id,
                "user_name": str(message.author),
                "channel_id": message.channel.id,
                "message_id": message.id,
                "guild_id": message.guild.id if message.guild else None
            }
            
            # Add to queue
            await self.add_to_queue(command_entry)
            
            # Confirm receipt
            await message.add_reaction('✅')
            await message.reply(f"Command queued: `{sanitized_command}`", mention_author=False)
            
            logger.info(f'Queued command from {message.author}: {sanitized_command}')
            
        except Exception as e:
            logger.error(f'Error queuing command: {e}')
            await message.add_reaction('❌')

    def sanitize_command(self, command: str) -> str:
        """Sanitize command text to prevent dangerous operations"""
        # Remove potentially dangerous characters and commands
        dangerous_patterns = [
            'rm -rf', 'sudo', 'su ', 'chmod 777', 'wget', 'curl',
            '>', '>>', '|', '&', ';', '$(', '`', 'eval', 'exec'
        ]
        
        sanitized = command.strip()
        
        # Check for dangerous patterns
        for pattern in dangerous_patterns:
            if pattern in sanitized.lower():
                logger.warning(f'Dangerous pattern detected: {pattern}')
                # Replace with safe version or remove
                sanitized = sanitized.replace(pattern, '[REMOVED]')
        
        # Limit length
        if len(sanitized) > 500:
            sanitized = sanitized[:500] + '...'
            
        return sanitized

    async def add_to_queue(self, command_entry: dict):
        """Add command to the queue file"""
        try:
            # Read existing queue
            queue = []
            if COMMAND_QUEUE_FILE.exists():
                with open(COMMAND_QUEUE_FILE, 'r') as f:
                    queue = json.load(f)
            
            # Add new command
            queue.append(command_entry)
            
            # Keep only last 100 commands
            if len(queue) > 100:
                queue = queue[-100:]
            
            # Write back to file
            with open(COMMAND_QUEUE_FILE, 'w') as f:
                json.dump(queue, f, indent=2)
                
        except Exception as e:
            logger.error(f'Error adding to queue: {e}')
            raise

async def main():
    """Main function to run the bot"""
    if not DISCORD_BOT_TOKEN:
        logger.error('DISCORD_BOT_TOKEN not found in environment variables or .env file')
        return
    
    bot = ClaudeCommandBot()
    
    try:
        await bot.start(DISCORD_BOT_TOKEN)
    except discord.LoginFailure:
        logger.error('Invalid Discord bot token')
    except Exception as e:
        logger.error(f'Error starting bot: {e}')
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())