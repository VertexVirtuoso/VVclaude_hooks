#!/usr/bin/env python3
"""
Test script to verify hooks are working correctly.
"""

import subprocess
import json
import sys
from pathlib import Path

def test_notification_hook():
    """Test the notification hook"""
    print("Testing notification hook...")
    
    # Create test input with enhanced data
    test_input = {
        "session_id": "test-session-123",
        "duration": 42,
        "tools_used": ["Edit", "Bash", "Write", "Read"],
        "files_modified": ["test.py", "config.json"]
    }
    
    # Run the notification script
    try:
        result = subprocess.run(
            ["uv", "run", "python3", "notification.py"],
            input=json.dumps(test_input),
            text=True,
            capture_output=True,
            cwd=Path(__file__).parent
        )
        
        print(f"Return code: {result.returncode}")
        if result.stdout:
            print("Stdout (last 500 chars):")
            print(result.stdout[-500:])
        if result.stderr:
            print("Stderr:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ Notification hook executed successfully!")
        else:
            print("❌ Notification hook failed!")
            
    except Exception as e:
        print(f"❌ Error running notification hook: {e}")

def test_stop_hook():
    """Test the stop hook"""
    print("\nTesting stop hook...")
    
    # Create test input with enhanced data
    test_input = {
        "session_id": "test-session-456",
        "reason": "User requested stop",
        "duration": 15
    }
    
    # Run the stop script
    try:
        result = subprocess.run(
            ["uv", "run", "python3", "stop.py"],
            input=json.dumps(test_input),
            text=True,
            capture_output=True,
            cwd=Path(__file__).parent
        )
        
        print(f"Return code: {result.returncode}")
        if result.stdout:
            print("Stdout (last 500 chars):")
            print(result.stdout[-500:])
        if result.stderr:
            print("Stderr:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ Stop hook executed successfully!")
        else:
            print("❌ Stop hook failed!")
            
    except Exception as e:
        print(f"❌ Error running stop hook: {e}")

def check_hook_configuration():
    """Check Claude Code hook configuration"""
    print("\nChecking hook configuration...")
    
    settings_file = Path.home() / ".claude" / "settings.json"
    
    if settings_file.exists():
        try:
            with open(settings_file, 'r') as f:
                settings = json.load(f)
                
            if "hooks" in settings:
                print("✅ Hook configuration found!")
                for hook_type in settings["hooks"]:
                    print(f"  - {hook_type}: {len(settings['hooks'][hook_type])} hook(s)")
            else:
                print("❌ No hooks configured in settings.json")
                
        except Exception as e:
            print(f"❌ Error reading settings.json: {e}")
    else:
        print("❌ Settings file not found")

def check_dependencies():
    """Check if dependencies are installed"""
    print("\nChecking dependencies...")
    
    try:
        import requests
        print("✅ requests library available")
    except ImportError:
        print("❌ requests library not available")
        
    try:
        import discord
        print("✅ discord.py library available")
    except ImportError:
        print("❌ discord.py library not available")

if __name__ == "__main__":
    print("🚀 Testing Claude Code hooks setup")
    print("=" * 50)
    
    check_dependencies()
    check_hook_configuration()
    test_notification_hook()
    test_stop_hook()
    
    print("\n" + "=" * 50)
    print("✅ Hook testing complete!")
    print("\nNow try running a Claude Code command to see the hooks in action!")