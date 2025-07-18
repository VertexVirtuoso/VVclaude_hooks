#!/usr/bin/env python3
"""
Interactive Discord bot setup script.
Guides users through configuring the bot token and user ID.
"""

import os
import sys
from pathlib import Path
import re

def get_env_file_path():
    """Get the path to the .env file"""
    env_path = Path.home() / ".claude" / "hooks" / ".env"
    return env_path

def read_env_file(env_path):
    """Read current .env file content"""
    if env_path.exists():
        with open(env_path, 'r') as f:
            return f.read()
    return ""

def write_env_file(env_path, content):
    """Write content to .env file"""
    env_path.parent.mkdir(parents=True, exist_ok=True)
    with open(env_path, 'w') as f:
        f.write(content)

def update_env_variable(content, key, value):
    """Update or add an environment variable in the content"""
    pattern = rf'^{key}=.*$'
    replacement = f'{key}={value}'
    
    if re.search(pattern, content, re.MULTILINE):
        # Update existing variable
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    else:
        # Add new variable
        if not content.endswith('\n') and content:
            content += '\n'
        content += f'{replacement}\n'
    
    return content

def validate_bot_token(token):
    """Basic bot token validation"""
    if not token or token == "YOUR_BOT_TOKEN_HERE":
        return False, "Invalid token"
    
    # Basic Discord bot token format check
    if len(token) < 50:
        return False, "Token too short"
    
    return True, "Token looks valid"

def validate_user_id(user_id):
    """Basic user ID validation"""
    if not user_id or user_id == "YOUR_USER_ID_HERE":
        return False, "Invalid user ID"
    
    try:
        user_id_int = int(user_id)
        if user_id_int < 100000000000000000:  # Discord IDs are 18+ digits
            return False, "User ID too short"
        return True, f"User ID looks valid"
    except ValueError:
        return False, "User ID must be numeric"

def main():
    """Main setup function"""
    print("🚀 Discord Bot Setup Assistant")
    print("=" * 50)
    
    # Check if setup guide exists
    setup_guide = Path("DISCORD_BOT_SETUP.md")
    if setup_guide.exists():
        print("📖 Setup guide available: DISCORD_BOT_SETUP.md")
        print("   Read it for detailed instructions!")
    
    print("\nThis script will help you configure your Discord bot.")
    print("You'll need:")
    print("1. Discord bot token (from Discord Developer Portal)")
    print("2. Your Discord user ID")
    print()
    
    # Get .env file path
    env_path = get_env_file_path()
    print(f"📁 Configuration file: {env_path}")
    
    # Read current .env content
    env_content = read_env_file(env_path)
    
    # Configure bot token
    print("\n🤖 Bot Token Configuration")
    print("-" * 30)
    
    current_token = ""
    if "DISCORD_BOT_TOKEN=" in env_content:
        # Extract current token (masked)
        for line in env_content.split('\n'):
            if line.startswith('DISCORD_BOT_TOKEN='):
                current_token = line.split('=', 1)[1]
                if current_token and current_token != "YOUR_BOT_TOKEN_HERE":
                    masked_token = current_token[:10] + "..." + current_token[-10:]
                    print(f"Current token: {masked_token}")
                break
    
    while True:
        if current_token and current_token != "YOUR_BOT_TOKEN_HERE":
            update_token = input("Update bot token? (y/n): ").lower().strip()
            if update_token != 'y':
                bot_token = current_token
                break
        
        print("\nEnter your Discord bot token:")
        print("(Get it from: https://discord.com/developers/applications)")
        bot_token = input("Bot token: ").strip()
        
        if not bot_token:
            print("❌ Bot token cannot be empty")
            continue
            
        valid, msg = validate_bot_token(bot_token)
        if valid:
            print(f"✅ {msg}")
            break
        else:
            print(f"❌ {msg}")
    
    # Configure user ID
    print("\n👤 User ID Configuration")
    print("-" * 30)
    
    current_user_id = ""
    if "AUTHORIZED_USER_ID=" in env_content:
        # Extract current user ID
        for line in env_content.split('\n'):
            if line.startswith('AUTHORIZED_USER_ID='):
                current_user_id = line.split('=', 1)[1]
                if current_user_id and current_user_id != "YOUR_USER_ID_HERE":
                    print(f"Current user ID: {current_user_id}")
                break
    
    while True:
        if current_user_id and current_user_id != "YOUR_USER_ID_HERE":
            update_user_id = input("Update user ID? (y/n): ").lower().strip()
            if update_user_id != 'y':
                user_id = current_user_id
                break
        
        print("\nEnter your Discord user ID:")
        print("(Right-click your name in Discord and 'Copy ID')")
        print("(Make sure Developer Mode is enabled in Discord settings)")
        user_id = input("User ID: ").strip()
        
        if not user_id:
            print("❌ User ID cannot be empty")
            continue
            
        valid, msg = validate_user_id(user_id)
        if valid:
            print(f"✅ {msg}")
            break
        else:
            print(f"❌ {msg}")
    
    # Update .env file
    print("\n💾 Saving Configuration")
    print("-" * 30)
    
    # Update environment variables
    env_content = update_env_variable(env_content, "DISCORD_BOT_TOKEN", bot_token)
    env_content = update_env_variable(env_content, "AUTHORIZED_USER_ID", user_id)
    
    try:
        write_env_file(env_path, env_content)
        print(f"✅ Configuration saved to {env_path}")
    except Exception as e:
        print(f"❌ Error saving configuration: {e}")
        return False
    
    # Validate configuration
    print("\n🔍 Validating Configuration")
    print("-" * 30)
    
    try:
        # Run validation script
        import subprocess
        result = subprocess.run([sys.executable, "validate_bot_config.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Configuration validation passed!")
        else:
            print("❌ Configuration validation failed")
            print(result.stdout)
            return False
            
    except Exception as e:
        print(f"⚠️  Could not run validation: {e}")
    
    # Next steps
    print("\n🎉 Setup Complete!")
    print("=" * 50)
    print("Next steps:")
    print("1. Make sure your bot is added to your Discord server")
    print("2. Test the bot: python3 discord_bot.py")
    print("3. Start full system: python3 start_bidirectional.py")
    print("4. Send a test command in Discord: 'claude: hello'")
    print("\nNeed help? Check DISCORD_BOT_SETUP.md")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)