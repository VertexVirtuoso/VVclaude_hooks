#!/usr/bin/env python3
"""
Deep webhook debugging - shows exactly what's being sent and received.
"""

import requests
import json
from pathlib import Path

def load_webhook_raw():
    """Load webhook URL exactly as stored"""
    env_path = Path.home() / ".claude" / "hooks" / ".env"
    
    if not env_path.exists():
        return None, "No .env file found"
    
    try:
        with open(env_path, 'r') as f:
            content = f.read()
            
        for line in content.split('\n'):
            if line.startswith('DISCORD_WEBHOOK='):
                url = line.split('=', 1)[1]
                return url, "Found"
    except Exception as e:
        return None, f"Error reading file: {e}"
    
    return None, "DISCORD_WEBHOOK not found in .env"

def detailed_webhook_test():
    """Perform detailed webhook testing"""
    print("🔍 Deep Webhook Debug Analysis")
    print("=" * 50)
    
    # Load webhook URL
    webhook_url, status = load_webhook_raw()
    print(f"📄 Loading webhook: {status}")
    
    if not webhook_url:
        print("❌ Cannot proceed without webhook URL")
        return
    
    # Show exact URL details
    print(f"\n📋 Webhook URL Analysis:")
    print(f"   Raw URL: '{webhook_url}'")
    print(f"   Length: {len(webhook_url)} characters")
    print(f"   Starts with: '{webhook_url[:30]}...'")
    print(f"   Ends with: '...{webhook_url[-20:]}'")
    
    # Check for hidden characters
    if webhook_url != webhook_url.strip():
        print("⚠️  WARNING: URL has leading/trailing whitespace!")
        webhook_url = webhook_url.strip()
        print(f"   Cleaned URL: '{webhook_url}'")
    
    # Parse webhook components
    if webhook_url.startswith('https://discord.com/api/webhooks/'):
        path = webhook_url.replace('https://discord.com/api/webhooks/', '')
        parts = path.split('/')
        
        if len(parts) == 2:
            webhook_id, webhook_token = parts
            print(f"\n🔢 Webhook Components:")
            print(f"   ID: {webhook_id}")
            print(f"   Token Length: {len(webhook_token)} chars")
            print(f"   Token Start: {webhook_token[:10]}...")
            print(f"   Token End: ...{webhook_token[-10:]}")
        else:
            print(f"❌ Invalid URL structure - found {len(parts)} parts, expected 2")
            return
    else:
        print("❌ URL doesn't start with expected Discord webhook prefix")
        return
    
    # Test different request methods
    print(f"\n🧪 Testing Different Request Approaches:")
    
    # Test 1: Basic POST
    print("   1. Basic POST request...")
    try:
        response = requests.post(webhook_url, timeout=10)
        print(f"      Status: {response.status_code}")
        print(f"      Response: {response.text[:100]}")
    except Exception as e:
        print(f"      Error: {e}")
    
    # Test 2: GET request (should return webhook info)
    print("   2. GET request (webhook info)...")
    try:
        response = requests.get(webhook_url, timeout=10)
        print(f"      Status: {response.status_code}")
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"      Webhook Name: {data.get('name', 'N/A')}")
                print(f"      Channel ID: {data.get('channel_id', 'N/A')}")
                print(f"      Guild ID: {data.get('guild_id', 'N/A')}")
            except:
                print(f"      Response: {response.text[:100]}")
        else:
            print(f"      Response: {response.text[:100]}")
    except Exception as e:
        print(f"      Error: {e}")
    
    # Test 3: POST with minimal payload
    print("   3. POST with minimal payload...")
    try:
        payload = {"content": "Test message"}
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            webhook_url,
            data=json.dumps(payload),
            headers=headers,
            timeout=10
        )
        print(f"      Status: {response.status_code}")
        if response.status_code == 204:
            print("      ✅ SUCCESS! Message should appear in Discord!")
        else:
            print(f"      Response: {response.text[:200]}")
    except Exception as e:
        print(f"      Error: {e}")
    
    # Test 4: Different payload format
    print("   4. POST with form data...")
    try:
        payload = {"content": "Test message (form data)"}
        response = requests.post(webhook_url, data=payload, timeout=10)
        print(f"      Status: {response.status_code}")
        if response.status_code == 204:
            print("      ✅ SUCCESS! Message should appear in Discord!")
        else:
            print(f"      Response: {response.text[:200]}")
    except Exception as e:
        print(f"      Error: {e}")
    
    # Test 5: Check if URL is accessible at all
    print("   5. Basic connectivity test...")
    try:
        # Just try to connect to the endpoint
        response = requests.get(f"https://discord.com/api/webhooks/{webhook_id}", timeout=10)
        print(f"      Status: {response.status_code}")
        print(f"      Response: {response.text[:100]}")
    except Exception as e:
        print(f"      Error: {e}")

if __name__ == "__main__":
    detailed_webhook_test()