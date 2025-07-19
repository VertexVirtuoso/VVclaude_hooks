#!/usr/bin/env python3
"""
Discord webhook diagnostic script.
Tests webhook connectivity and identifies common issues.
"""

import requests
import json
import time
from pathlib import Path
from datetime import datetime

def load_discord_webhook():
    """Load Discord webhook from .env file"""
    env_paths = [
        Path.home() / ".claude" / "hooks" / ".env",
        Path("/home/charlie/.claude/hooks/.env"),
        Path.cwd() / ".env"
    ]
    
    for env_path in env_paths:
        if env_path.exists():
            try:
                with open(env_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('DISCORD_WEBHOOK='):
                            return line.split('=', 1)[1]
            except Exception as e:
                print(f"Error reading {env_path}: {e}")
    
    return None

def test_webhook_format(webhook_url):
    """Test if webhook URL format is valid"""
    if not webhook_url:
        return False, "No webhook URL provided"
    
    if not webhook_url.startswith('https://discord.com/api/webhooks/'):
        return False, "Invalid webhook URL format - must start with 'https://discord.com/api/webhooks/'"
    
    parts = webhook_url.replace('https://discord.com/api/webhooks/', '').split('/')
    if len(parts) != 2:
        return False, "Invalid webhook URL format - missing ID or token"
    
    webhook_id, webhook_token = parts
    
    if not webhook_id.isdigit():
        return False, "Invalid webhook ID - must be numeric"
    
    if len(webhook_token) < 50:
        return False, "Invalid webhook token - too short"
    
    return True, f"Webhook format looks valid (ID: {webhook_id})"

def test_webhook_connectivity(webhook_url):
    """Test basic connectivity to Discord"""
    try:
        # Test basic connectivity to Discord
        response = requests.get("https://discord.com", timeout=10)
        if response.status_code != 200:
            return False, f"Cannot reach Discord (status: {response.status_code})"
        return True, "Discord is reachable"
    except requests.exceptions.Timeout:
        return False, "Timeout connecting to Discord"
    except requests.exceptions.ConnectionError:
        return False, "Network connection error"
    except Exception as e:
        return False, f"Unexpected error: {e}"

def test_webhook_endpoint(webhook_url):
    """Test the specific webhook endpoint"""
    try:
        # Send a simple test message
        payload = {
            "content": f"🔍 **Webhook Test** - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        }
        headers = {"Content-Type": "application/json"}
        
        print(f"🔄 Sending test message to webhook...")
        response = requests.post(
            webhook_url,
            data=json.dumps(payload),
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 204:
            return True, "Test message sent successfully!"
        elif response.status_code == 404:
            return False, "Webhook not found (404) - webhook may have been deleted"
        elif response.status_code == 401:
            return False, "Unauthorized (401) - webhook token is invalid"
        elif response.status_code == 429:
            retry_after = response.headers.get('retry-after', 'unknown')
            return False, f"Rate limited (429) - retry after {retry_after} seconds"
        else:
            try:
                error_data = response.json()
                return False, f"Error {response.status_code}: {error_data.get('message', 'Unknown error')}"
            except:
                return False, f"Error {response.status_code}: {response.text[:100]}"
                
    except requests.exceptions.Timeout:
        return False, "Request timeout - webhook endpoint not responding"
    except requests.exceptions.ConnectionError:
        return False, "Connection error - cannot reach webhook endpoint"
    except Exception as e:
        return False, f"Unexpected error: {e}"

def analyze_webhook_url(webhook_url):
    """Analyze webhook URL for common issues"""
    issues = []
    
    # Check for common formatting issues
    if ' ' in webhook_url:
        issues.append("Webhook URL contains spaces")
    
    if webhook_url.endswith('/'):
        issues.append("Webhook URL ends with trailing slash")
    
    if 'YOUR_' in webhook_url:
        issues.append("Webhook URL contains placeholder text")
    
    # Extract webhook info
    if webhook_url.startswith('https://discord.com/api/webhooks/'):
        parts = webhook_url.replace('https://discord.com/api/webhooks/', '').split('/')
        if len(parts) == 2:
            webhook_id, webhook_token = parts
            
            # Mask the token for display
            if len(webhook_token) > 10:
                masked_token = webhook_token[:5] + "..." + webhook_token[-5:]
            else:
                masked_token = "***"
                
            print(f"📋 Webhook ID: {webhook_id}")
            print(f"🔐 Webhook Token: {masked_token}")
    
    return issues

def main():
    """Main diagnostic function"""
    print("🔍 Discord Webhook Diagnostic Tool")
    print("=" * 50)
    
    # Load webhook URL
    print("\n📄 Loading webhook URL...")
    webhook_url = load_discord_webhook()
    
    if not webhook_url:
        print("❌ No webhook URL found in .env file")
        print("   Please check that DISCORD_WEBHOOK is set in .env")
        return False
    
    print(f"✅ Webhook URL loaded from .env")
    
    # Analyze webhook URL
    print("\n🔍 Analyzing webhook URL...")
    issues = analyze_webhook_url(webhook_url)
    
    if issues:
        print("⚠️  Issues found:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("✅ No obvious URL formatting issues")
    
    # Test webhook format
    print("\n🧪 Testing webhook format...")
    format_valid, format_msg = test_webhook_format(webhook_url)
    
    if format_valid:
        print(f"✅ {format_msg}")
    else:
        print(f"❌ {format_msg}")
        return False
    
    # Test basic connectivity
    print("\n🌐 Testing Discord connectivity...")
    conn_valid, conn_msg = test_webhook_connectivity(webhook_url)
    
    if conn_valid:
        print(f"✅ {conn_msg}")
    else:
        print(f"❌ {conn_msg}")
        return False
    
    # Test webhook endpoint
    print("\n🎯 Testing webhook endpoint...")
    webhook_valid, webhook_msg = test_webhook_endpoint(webhook_url)
    
    if webhook_valid:
        print(f"✅ {webhook_msg}")
        print("🎉 Webhook is working correctly!")
        print("\nIf you don't see the test message in Discord:")
        print("1. Check the correct channel")
        print("2. Verify webhook permissions")
        print("3. Make sure the webhook wasn't moved/deleted")
        return True
    else:
        print(f"❌ {webhook_msg}")
        
        # Provide specific help based on error
        if "404" in webhook_msg:
            print("\n🔧 Troubleshooting suggestions:")
            print("1. The webhook may have been deleted")
            print("2. Create a new webhook in Discord:")
            print("   - Go to channel settings")
            print("   - Webhooks → Create Webhook")
            print("   - Copy the webhook URL")
            print("   - Update your .env file")
        elif "401" in webhook_msg:
            print("\n🔧 Troubleshooting suggestions:")
            print("1. The webhook token is invalid")
            print("2. Check your .env file for typos")
            print("3. Generate a new webhook if needed")
        elif "429" in webhook_msg:
            print("\n🔧 Troubleshooting suggestions:")
            print("1. You're being rate limited")
            print("2. Wait a few minutes before trying again")
            print("3. Reduce notification frequency if needed")
        
        return False

if __name__ == "__main__":
    success = main()
    print("\n" + "=" * 50)
    if success:
        print("✅ Webhook diagnosis complete - everything working!")
    else:
        print("❌ Webhook diagnosis complete - issues found!")
        print("💡 Fix the issues above and run the script again")
    
    exit(0 if success else 1)