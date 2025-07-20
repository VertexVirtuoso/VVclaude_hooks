#!/usr/bin/env python3
"""
Claude Code analysis start hook - plays sound only, no Discord notification.
Used when Claude Code begins analyzing code or files.
"""

import json
from sound_manager import SoundManager

# Initialize sound manager
sound_manager = SoundManager()

# Main logic
if __name__ == "__main__":
    print("🔍 Claude Code analysis start hook")
    
    # Get session info from Claude (passed via stdin as JSON)
    try:
        hook_input = json.loads(input())
        print(f"📨 Received hook input: {json.dumps(hook_input, indent=2)}")
    except json.JSONDecodeError:
        print("⚠️ No valid JSON input received, using default values")
        hook_input = {"session_id": "unknown"}
    
    # Play thinking sound for analysis start
    print("🔊 Playing analysis start sound...")
    sound_manager.play_sound("thinking")
    
    # Exit successfully
    print("🎯 Analysis start hook completed")
    exit(0)