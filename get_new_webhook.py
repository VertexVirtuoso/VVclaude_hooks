#!/usr/bin/env python3
"""
Helper to get new webhook URL from Discord.
"""

import re
from pathlib import Path

def show_how_to_get_webhook():
    """Show exactly how to get the current webhook URL"""
    print("🔧 How to Get Your Current Webhook URL")
    print("=" * 45)
    print()
    print("Your webhook exists but the token changed. Here's how to get the new URL:")
    print()
    print("📋 Step-by-Step:")
    print("1. Go to your Discord server")
    print("2. Find the channel where you want notifications")
    print("3. Right-click the channel → 'Edit Channel'")
    print("4. Click 'Integrations' tab")
    print("5. Look for 'Webhooks' section")
    print("6. You should see an existing webhook")
    print("7. Click 'Copy Webhook URL' (or create new if needed)")
    print()
    print("The URL should look like:")
    print("https://discord.com/api/webhooks/NUMBERS/LETTERS_AND_NUMBERS")
    print()
    print("🔍 What to look for:")
    print("- The webhook name might be something like 'Claude Code' or default name")
    print("- The webhook ID (numbers) might be the same: 1395702045385822290")
    print("- But the token (letters/numbers after) will be different")
    print()

def update_webhook_interactive():
    """Interactive webhook URL update"""
    print("📝 Update Webhook URL")
    print("-" * 25)
    print()
    
    # Get current webhook info
    env_file = Path.home() / ".claude" / "hooks" / ".env"
    current_id = "1395702045385822290"
    
    print(f"Current webhook ID: {current_id}")
    print("(This should stay the same if you're using the same webhook)")
    print()
    
    while True:
        new_url = input("Paste your new webhook URL here: ").strip()
        
        if not new_url:
            print("❌ Please provide a webhook URL")
            continue
        
        # Validate format
        if not new_url.startswith('https://discord.com/api/webhooks/'):
            print("❌ Invalid format. Should start with: https://discord.com/api/webhooks/")
            continue
        
        # Extract components
        try:
            parts = new_url.replace('https://discord.com/api/webhooks/', '').split('/')
            if len(parts) != 2:
                print("❌ Invalid URL format")
                continue
            
            new_id, new_token = parts
            
            if not new_id.isdigit():
                print("❌ Invalid webhook ID")
                continue
            
            if len(new_token) < 50:
                print("❌ Token seems too short")
                continue
            
            print(f"✅ Webhook looks valid!")
            print(f"   ID: {new_id}")
            print(f"   Token: {new_token[:10]}...{new_token[-10:]}")
            
            if new_id == current_id:
                print("✅ Same webhook ID - this is probably the refreshed token!")
            else:
                print("ℹ️  Different webhook ID - you created a new webhook")
            
            break
            
        except Exception as e:
            print(f"❌ Error parsing URL: {e}")
            continue
    
    # Update .env file
    try:
        # Read current .env
        if env_file.exists():
            with open(env_file, 'r') as f:
                content = f.read()
        else:
            content = ""
        
        # Update DISCORD_WEBHOOK line
        webhook_pattern = r'^DISCORD_WEBHOOK=.*$'
        new_line = f'DISCORD_WEBHOOK={new_url}'
        
        if re.search(webhook_pattern, content, re.MULTILINE):
            content = re.sub(webhook_pattern, new_line, content, flags=re.MULTILINE)
        else:
            if content and not content.endswith('\n'):
                content += '\n'
            content += new_line + '\n'
        
        # Write back
        with open(env_file, 'w') as f:
            f.write(content)
        
        print(f"✅ Updated {env_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")
        return False

def test_new_webhook():
    """Test the updated webhook"""
    print("\n🧪 Testing Updated Webhook")
    print("-" * 30)
    
    try:
        import subprocess
        result = subprocess.run(
            ["uv", "run", "python3", "deep_webhook_debug.py"],
            capture_output=True,
            text=True
        )
        
        if "✅ SUCCESS!" in result.stdout:
            print("🎉 SUCCESS! Your webhook is working!")
            print("You should have received test messages in Discord.")
            return True
        else:
            print("❌ Still having issues. Here's the debug output:")
            print(result.stdout[-500:])  # Last 500 chars
            return False
            
    except Exception as e:
        print(f"❌ Error testing: {e}")
        return False

def main():
    """Main function"""
    print("🔍 Webhook Token Issue Detected")
    print()
    print("Your webhook ID exists but the token is invalid.")
    print("This happens when Discord regenerates the webhook token.")
    print()
    
    show_how_to_get_webhook()
    
    proceed = input("Do you have the new webhook URL ready? (y/n): ").lower().strip()
    
    if proceed == 'y':
        if update_webhook_interactive():
            test_new_webhook()
    else:
        print("\nℹ️  Get your webhook URL from Discord first, then run:")
        print("   python3 get_new_webhook.py")

if __name__ == "__main__":
    main()