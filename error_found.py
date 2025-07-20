#!/usr/bin/env python3
"""
Claude Code error found hook - plays sound only, no Discord notification.
Used when Claude Code discovers errors or issues during analysis.
"""

import json
from sound_manager import SoundManager

# Initialize sound manager
sound_manager = SoundManager()

# Main logic
if __name__ == "__main__":
    print("❌ Claude Code error found hook")
    
    # Get session info from Claude (passed via stdin as JSON)
    try:
        hook_input = json.loads(input())
        print(f"📨 Received hook input: {json.dumps(hook_input, indent=2)}")
    except json.JSONDecodeError:
        print("⚠️ No valid JSON input received, using default values")
        hook_input = {"session_id": "unknown"}
    
    # Play error found sound (randomly selected from available options)
    print("🔊 Playing error found sound...")
    sound_manager.play_sound("error_found")
    
    # Exit successfully
    print("🎯 Error found hook completed")
    exit(0)