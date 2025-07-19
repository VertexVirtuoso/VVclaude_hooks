#!/usr/bin/env python3
import os
import platform
import subprocess
import requests
import json
import time
from pathlib import Path
from datetime import datetime
from sound_manager import SoundManager

# Load Discord webhook from .env file
def load_discord_webhook():
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
    
    # Fallback to environment variable
    return os.getenv('DISCORD_WEBHOOK', '')

DISCORD_WEBHOOK_URL = load_discord_webhook()

# Initialize sound manager
sound_manager = SoundManager()

# Send Discord message with retry logic and rich formatting
def send_discord_message_with_retry(content, embed_data=None, max_retries=3):
    """Send Discord message with retry logic and rich formatting"""
    if not DISCORD_WEBHOOK_URL:
        print("No Discord webhook URL found. Skipping Discord notification.")
        return False
    
    # Prepare payload with rich formatting
    payload = {"content": content}
    
    if embed_data:
        payload["embeds"] = [embed_data]
    
    headers = {"Content-Type": "application/json"}
    
    # Retry logic
    for attempt in range(max_retries):
        try:
            response = requests.post(
                DISCORD_WEBHOOK_URL, 
                data=json.dumps(payload), 
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 204:
                print(f"✅ Discord notification sent successfully (attempt {attempt + 1})")
                return True
            elif response.status_code == 429:
                # Rate limited, wait and retry
                retry_after = response.headers.get('retry-after', 1)
                print(f"⏳ Rate limited, waiting {retry_after}s before retry...")
                time.sleep(float(retry_after))
                continue
            else:
                print(f"❌ Discord API error (attempt {attempt + 1}): {response.status_code} - {response.text}")
                
        except requests.exceptions.Timeout:
            print(f"⏰ Request timeout (attempt {attempt + 1})")
        except requests.exceptions.ConnectionError:
            print(f"🔌 Connection error (attempt {attempt + 1})")
        except Exception as e:
            print(f"❌ Unexpected error (attempt {attempt + 1}): {e}")
        
        # Wait before retry (exponential backoff)
        if attempt < max_retries - 1:
            wait_time = 2 ** attempt
            print(f"⏳ Waiting {wait_time}s before retry...")
            time.sleep(wait_time)
    
    print(f"❌ Failed to send Discord message after {max_retries} attempts")
    return False

def gather_system_context():
    """Gather system and environment context"""
    context = {
        "timestamp": datetime.now().isoformat(),
        "hostname": platform.node(),
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "working_directory": str(Path.cwd()),
        "user": os.getenv("USER", "unknown"),
    }
    
    # Try to get git information
    try:
        git_branch = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if git_branch.returncode == 0:
            context["git_branch"] = git_branch.stdout.strip()
        
        git_status = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if git_status.returncode == 0:
            changed_files = git_status.stdout.strip().split('\n') if git_status.stdout.strip() else []
            context["git_changes"] = len(changed_files)
            context["git_files"] = changed_files[:5]  # Limit to first 5 files
    except:
        pass
    
    # Try to get project information
    try:
        project_files = ["package.json", "pyproject.toml", "Cargo.toml", "go.mod", "composer.json"]
        for file in project_files:
            if Path(file).exists():
                context["project_type"] = file
                break
    except:
        pass
    
    return context

def analyze_task_type(hook_input, context):
    """Analyze session data to determine task type and appropriate sound"""
    try:
        # Get any available context
        session_id = hook_input.get('session_id', '')
        tools_used = hook_input.get('tools_used', [])
        working_dir = context.get('working_directory', '')
        
        # Convert tools to string for analysis
        tools_str = ' '.join(tools_used) if isinstance(tools_used, list) else str(tools_used)
        
        # Analyze for research/analysis activities
        research_keywords = [
            'search', 'find', 'analyze', 'research', 'investigate', 'explore',
            'understand', 'explain', 'review', 'examine', 'study', 'grep',
            'glob', 'read', 'check', 'inspect', 'discover', 'identify',
            'Grep', 'Read', 'LS', 'Task', 'WebFetch', 'WebSearch'
        ]
        
        # Analyze for implementation activities  
        implementation_keywords = [
            'implement', 'create', 'build', 'develop', 'write', 'code',
            'add', 'modify', 'update', 'fix', 'refactor', 'enhance',
            'install', 'setup', 'configure', 'deploy', 'commit',
            'Edit', 'MultiEdit', 'Write', 'NotebookEdit'
        ]
        
        # Analyze for testing activities
        testing_keywords = [
            'test', 'run', 'execute', 'validate', 'verify', 'check',
            'debug', 'troubleshoot', 'diagnose', 'Bash'
        ]
        
        # Convert to lowercase for comparison
        text_to_analyze = f"{session_id} {tools_str} {working_dir}".lower()
        
        # Count keyword matches
        research_score = sum(1 for word in research_keywords if word.lower() in text_to_analyze)
        implementation_score = sum(1 for word in implementation_keywords if word.lower() in text_to_analyze)
        testing_score = sum(1 for word in testing_keywords if word.lower() in text_to_analyze)
        
        print(f"🔍 Task analysis: Research={research_score}, Implementation={implementation_score}, Testing={testing_score}")
        print(f"📝 Analyzed text: {text_to_analyze[:100]}...")
        
        # Determine primary task type
        if implementation_score > research_score and implementation_score > testing_score:
            return "implementation_complete"
        elif testing_score > research_score and testing_score > implementation_score:
            return "testing_complete"
        elif research_score > 0:
            return "research_complete"
        else:
            # Default to implementation for general completion
            return "implementation_complete"
            
    except Exception as e:
        print(f"❌ Error analyzing task type: {e}")
        return "success"  # fallback

def create_rich_notification(hook_input, context, task_type="implementation_complete"):
    """Create rich notification with context"""
    session_id = hook_input.get("session_id", "unknown")
    
    # Create task-specific message
    task_messages = {
        "research_complete": "🔍 **Claude Code Research Completed!**",
        "implementation_complete": "⚙️ **Claude Code Implementation Completed!**", 
        "analysis_complete": "📊 **Claude Code Analysis Completed!**",
        "testing_complete": "🧪 **Claude Code Testing Completed!**",
        "success": "🎉 **Claude Code Task Completed!**"
    }
    
    main_message = task_messages.get(task_type, task_messages["success"])
    
    # Create embed with detailed information
    embed = {
        "title": "Task Completion Details",
        "color": 0x00ff00,  # Green color
        "timestamp": context["timestamp"],
        "fields": [
            {
                "name": "📋 Session ID",
                "value": f"`{session_id}`",
                "inline": True
            },
            {
                "name": "🖥️ System",
                "value": f"`{context['hostname']}`",
                "inline": True
            },
            {
                "name": "📁 Directory",
                "value": f"`{os.path.basename(context['working_directory'])}`",
                "inline": True
            }
        ],
        "footer": {
            "text": f"Claude Code Hooks • {context['user']}"
        }
    }
    
    # Add git information if available
    if context.get("git_branch"):
        embed["fields"].append({
            "name": "🌿 Git Branch",
            "value": f"`{context['git_branch']}`",
            "inline": True
        })
    
    if context.get("git_changes", 0) > 0:
        embed["fields"].append({
            "name": "📝 Changed Files",
            "value": f"{context['git_changes']} file(s) modified",
            "inline": True
        })
    
    # Add project type if detected
    if context.get("project_type"):
        embed["fields"].append({
            "name": "🚀 Project Type",
            "value": f"`{context['project_type']}`",
            "inline": True
        })
    
    # Add additional context from hook input
    if hook_input.get("duration"):
        embed["fields"].append({
            "name": "⏱️ Duration",
            "value": f"{hook_input['duration']}s",
            "inline": True
        })
    
    if hook_input.get("tools_used"):
        tools = hook_input["tools_used"]
        if isinstance(tools, list):
            embed["fields"].append({
                "name": "🔧 Tools Used",
                "value": f"`{', '.join(tools[:3])}`" + (f" +{len(tools)-3} more" if len(tools) > 3 else ""),
                "inline": True
            })
    
    return main_message, embed

# Main logic
if __name__ == "__main__":
    print("🚀 Claude Code notification hook started")
    
    # Get session info from Claude (passed via stdin as JSON)
    try:
        hook_input = json.loads(input())
        print(f"📨 Received hook input: {json.dumps(hook_input, indent=2)}")
    except json.JSONDecodeError:
        print("⚠️ No valid JSON input received, using default values")
        hook_input = {"session_id": "unknown"}
    
    # Gather system context
    print("🔍 Gathering system context...")
    context = gather_system_context()
    
    # Analyze task type for appropriate sound
    print("🔍 Analyzing task type...")
    sound_type = analyze_task_type(hook_input, context)
    print(f"🎵 Selected sound type: {sound_type}")
    
    # Create rich notification
    print("✨ Creating rich notification...")
    main_message, embed = create_rich_notification(hook_input, context, sound_type)
    
    # Play appropriate sound based on task type
    print(f"🔊 Playing {sound_type} notification sound...")
    sound_manager.play_sound(sound_type)
    
    # Send Discord message with retry logic
    print("📤 Sending Discord notification...")
    success = send_discord_message_with_retry(main_message, embed)
    
    if success:
        print("✅ Notification sent successfully!")
    else:
        print("❌ Failed to send notification, but continuing...")
    
    # Exit successfully
    print("🎯 Notification hook completed")
    exit(0)
