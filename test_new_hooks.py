#!/usr/bin/env python3
"""
Test script for the new audio hooks system.
"""

import json
import subprocess
import time

def test_hook(hook_script, test_name):
    """Test a specific hook script"""
    print(f"\n🧪 Testing {test_name}...")
    
    test_input = {
        "session_id": f"test-{test_name}",
        "tools_used": ["test"],
        "duration": 1.5
    }
    
    try:
        # Run the hook script with test input
        process = subprocess.run(
            ["python3", hook_script],
            input=json.dumps(test_input),
            text=True,
            capture_output=True,
            timeout=10
        )
        
        if process.returncode == 0:
            print(f"✅ {test_name} completed successfully")
            print(f"📝 Output: {process.stdout.strip()}")
        else:
            print(f"❌ {test_name} failed with exit code {process.returncode}")
            print(f"📝 Error: {process.stderr.strip()}")
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {test_name} timed out")
    except Exception as e:
        print(f"❌ {test_name} error: {e}")

def main():
    """Test all hook scripts"""
    print("🎵 Testing New Audio Hooks System")
    print("=" * 40)
    
    hooks_to_test = [
        ("task_start.py", "Task Start Hook"),
        ("thinking.py", "Thinking Hook"), 
        ("error_found.py", "Error Found Hook"),
        ("analysis_start.py", "Analysis Start Hook"),
        ("notification.py", "Main Notification Hook")
    ]
    
    for hook_file, test_name in hooks_to_test:
        test_hook(hook_file, test_name)
        time.sleep(1)  # Brief pause between tests
    
    print(f"\n🎯 All hook tests completed!")
    print("\n📋 Hook Usage Guide:")
    print("- notification.py: Task completion (with Discord notification)")
    print("- task_start.py: Starting difficult tasks (sound only)")
    print("- thinking.py: Processing/thinking (sound only)")
    print("- error_found.py: Error detection (sound only)")
    print("- analysis_start.py: Beginning analysis (sound only)")

if __name__ == "__main__":
    main()