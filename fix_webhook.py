#!/usr/bin/env python3
"""
Discord webhook fix helper.
Guides user through creating a new webhook and updating configuration.
"""

import re
from pathlib import Path

def show_webhook_instructions():
    """Show step-by-step webhook creation instructions"""
    print("🔧 Discord Webhook Fix Guide")
    print("=" * 40)
    print()
    print("Your webhook was deleted or is invalid. Here's how to fix it:")
    print()
    print("📋 Step 1: Create a New Webhook")
    print("   1. Go to your Discord server")
    print("   2. Right-click the channel where you want notifications")
    print("   3. Click 'Edit Channel'")
    print("   4. Go to 'Integrations' tab")
    print("   5. Click 'Webhooks' → 'Create Webhook'")
    print("   6. Give it a name (e.g., 'Claude Code Notifications')")
    print("   7. Copy the webhook URL")
    print()
    print("🔗 Step 2: Update Your Configuration")
    print("   The webhook URL should look like:")
    print("   https://discord.com/api/webhooks/1234567890/abcdef...")
    print()

def update_webhook_url():
    """Interactive webhook URL update"""
    env_file = Path.home() / ".claude" / "hooks" / ".env"
    
    print("📝 Update Webhook URL")
    print("-" * 30)
    
    # Get new webhook URL
    while True:
        webhook_url = input("Enter your new Discord webhook URL: ").strip()
        
        if not webhook_url:
            print("❌ Webhook URL cannot be empty")
            continue
        
        # Validate format
        if not webhook_url.startswith('https://discord.com/api/webhooks/'):
            print("❌ Invalid webhook URL format")
            print("   Must start with: https://discord.com/api/webhooks/")
            continue
        
        parts = webhook_url.replace('https://discord.com/api/webhooks/', '').split('/')
        if len(parts) != 2:
            print("❌ Invalid webhook URL format")
            print("   Should be: https://discord.com/api/webhooks/ID/TOKEN")
            continue
        
        webhook_id, webhook_token = parts
        if not webhook_id.isdigit() or len(webhook_token) < 50:
            print("❌ Invalid webhook format")
            continue
        
        print("✅ Webhook URL format looks valid!")
        break
    
    # Update .env file
    try:
        if env_file.exists():
            with open(env_file, 'r') as f:
                content = f.read()
        else:
            content = ""
        
        # Update or add DISCORD_WEBHOOK
        webhook_pattern = r'^DISCORD_WEBHOOK=.*$'
        webhook_line = f'DISCORD_WEBHOOK={webhook_url}'
        
        if re.search(webhook_pattern, content, re.MULTILINE):
            # Update existing
            content = re.sub(webhook_pattern, webhook_line, content, flags=re.MULTILINE)
        else:
            # Add new
            if content and not content.endswith('\n'):
                content += '\n'
            content += webhook_line + '\n'
        
        # Write back
        with open(env_file, 'w') as f:
            f.write(content)
        
        print(f"✅ Webhook URL updated in {env_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")
        return False

def test_new_webhook():
    """Test the new webhook"""
    print("\n🧪 Testing New Webhook")
    print("-" * 30)
    
    try:
        import subprocess
        result = subprocess.run(
            ["uv", "run", "python3", "diagnose_webhook.py"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Webhook test passed!")
            print("🎉 Your Discord notifications should work now!")
            return True
        else:
            print("❌ Webhook test failed:")
            print(result.stdout)
            return False
            
    except Exception as e:
        print(f"❌ Error testing webhook: {e}")
        return False

def main():
    """Main function"""
    print("🚨 Discord Webhook Issue Detected")
    print()
    
    # Show instructions
    show_webhook_instructions()
    
    # Ask if user wants to update now
    update_now = input("Do you want to update the webhook URL now? (y/n): ").lower().strip()
    
    if update_now == 'y':
        if update_webhook_url():
            # Test the new webhook
            test_new_webhook()
        else:
            print("❌ Failed to update webhook URL")
    else:
        print("ℹ️  You can update the webhook URL later by:")
        print("   1. Running this script again")
        print("   2. Manually editing ~/.claude/hooks/.env")
        print("   3. Running: python3 diagnose_webhook.py")
    
    print("\n📖 Need help? Check DISCORD_BOT_SETUP.md for detailed instructions")

if __name__ == "__main__":
    main()