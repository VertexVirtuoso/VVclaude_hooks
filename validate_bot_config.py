#!/usr/bin/env python3
"""
Discord bot configuration validator.
Checks if bot token and user ID are properly configured.
"""

import os
import sys
from pathlib import Path
import json

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
            print(f"📄 Found .env file: {env_path}")
            try:
                with open(env_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if '=' in line and not line.startswith('#'):
                            key, value = line.split('=', 1)
                            env_vars[key] = value
                break
            except Exception as e:
                print(f"❌ Error reading {env_path}: {e}")
    
    return env_vars

def validate_bot_token(token):
    """Validate bot token format"""
    if not token:
        return False, "No bot token provided"
    
    if token == "YOUR_BOT_TOKEN_HERE":
        return False, "Bot token not configured (still using placeholder)"
    
    # Discord bot tokens have a specific format
    if not token.startswith(('MTI', 'MTA', 'ODc', 'ODY')):
        return False, "Invalid bot token format"
    
    if len(token) < 50:
        return False, "Bot token too short"
    
    return True, "Bot token format looks valid"

def validate_user_id(user_id):
    """Validate Discord user ID"""
    if not user_id:
        return False, "No user ID provided"
    
    if user_id == "YOUR_USER_ID_HERE":
        return False, "User ID not configured (still using placeholder)"
    
    try:
        user_id_int = int(user_id)
        if user_id_int < 100000000000000000:  # Discord IDs are 18+ digits
            return False, "User ID too short (invalid Discord ID)"
        return True, f"User ID format looks valid ({user_id})"
    except ValueError:
        return False, "User ID must be numeric"

def check_dependencies():
    """Check if required dependencies are available"""
    try:
        import discord
        print("✅ discord.py library is available")
        print(f"   Version: {discord.__version__}")
        return True
    except ImportError:
        print("❌ discord.py library not found")
        print("   Run: uv sync")
        return False

def main():
    """Main validation function"""
    print("🔍 Discord Bot Configuration Validator")
    print("=" * 50)
    
    # Check dependencies
    print("\n📦 Checking Dependencies...")
    deps_ok = check_dependencies()
    
    # Load environment variables
    print("\n🔧 Loading Configuration...")
    env_vars = load_env_vars()
    
    if not env_vars:
        print("❌ No .env file found or unable to read configuration")
        print("   Create .env file with DISCORD_BOT_TOKEN and AUTHORIZED_USER_ID")
        return False
    
    # Validate bot token
    print("\n🤖 Validating Bot Token...")
    bot_token = env_vars.get('DISCORD_BOT_TOKEN')
    token_valid, token_msg = validate_bot_token(bot_token)
    
    if token_valid:
        print(f"✅ {token_msg}")
        # Mask the token for security
        masked_token = bot_token[:10] + "..." + bot_token[-10:]
        print(f"   Token: {masked_token}")
    else:
        print(f"❌ {token_msg}")
    
    # Validate user ID
    print("\n👤 Validating User ID...")
    user_id = env_vars.get('AUTHORIZED_USER_ID')
    user_valid, user_msg = validate_user_id(user_id)
    
    if user_valid:
        print(f"✅ {user_msg}")
    else:
        print(f"❌ {user_msg}")
    
    # Check webhook URL
    print("\n🔗 Checking Webhook URL...")
    webhook_url = env_vars.get('DISCORD_WEBHOOK')
    if webhook_url and webhook_url != "YOUR_WEBHOOK_URL_HERE":
        print("✅ Discord webhook URL is configured")
    else:
        print("❌ Discord webhook URL not configured")
    
    # Overall status
    print("\n" + "=" * 50)
    all_valid = deps_ok and token_valid and user_valid
    
    if all_valid:
        print("🎉 Configuration looks good! Ready to start the bot.")
        print("\nNext steps:")
        print("1. Start the bot: python3 discord_bot.py")
        print("2. Or start full system: python3 start_bidirectional.py")
        return True
    else:
        print("❌ Configuration issues found. Please fix the above errors.")
        print("\nSetup guide: cat DISCORD_BOT_SETUP.md")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)