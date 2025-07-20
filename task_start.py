#!/usr/bin/env python3
"""
Claude Code task start hook - plays sound only, no Discord notification.
Used when Claude Code starts working on a difficult or complex task.
"""

import json
from sound_manager import SoundManager

# Initialize sound manager
sound_manager = SoundManager()

# Main logic
if __name__ == "__main__":
    print("🚀 Claude Code task start hook")
    
    # Get session info from Claude (passed via stdin as JSON)
    try:
        hook_input = json.loads(input())
        print(f"📨 Received hook input: {json.dumps(hook_input, indent=2)}")
    except json.JSONDecodeError:
        print("⚠️ No valid JSON input received, using default values")
        hook_input = {"session_id": "unknown"}
    
    # Play task start sound
    print("🔊 Playing task start sound...")
    sound_manager.play_sound("task_start")
    
    # Exit successfully
    print("🎯 Task start hook completed")
    exit(0)