#!/usr/bin/env python3
"""
Monitor script for Claude Code command queue.
Watches for new commands and executes them via Claude Code.
"""

import os
import json
import time
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
COMMAND_QUEUE_FILE = Path.home() / ".claude" / "command_queue.json"
PROCESSED_COMMANDS_FILE = Path.home() / ".claude" / "processed_commands.json"
CLAUDE_CODE_COMMAND = "claude-code"  # Adjust if your claude-code is installed differently
POLL_INTERVAL = 2  # seconds
MAX_CONCURRENT_PROCESSES = 1  # Only run one Claude Code instance at a time

class ClaudeMonitor:
    def __init__(self):
        self.processed_commands = self.load_processed_commands()
        self.running_processes: Dict[str, subprocess.Popen] = {}
        
    def load_processed_commands(self) -> set:
        """Load list of already processed command IDs"""
        try:
            if PROCESSED_COMMANDS_FILE.exists():
                with open(PROCESSED_COMMANDS_FILE, 'r') as f:
                    data = json.load(f)
                    return set(data.get('processed_ids', []))
        except Exception as e:
            logger.error(f"Error loading processed commands: {e}")
        return set()
    
    def save_processed_commands(self):
        """Save list of processed command IDs"""
        try:
            PROCESSED_COMMANDS_FILE.parent.mkdir(parents=True, exist_ok=True)
            data = {
                'processed_ids': list(self.processed_commands),
                'last_updated': datetime.now().isoformat()
            }
            with open(PROCESSED_COMMANDS_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving processed commands: {e}")
    
    def get_command_id(self, command_entry: dict) -> str:
        """Generate unique ID for a command"""
        return f"{command_entry['timestamp']}_{command_entry['message_id']}"
    
    def load_command_queue(self) -> List[dict]:
        """Load pending commands from queue file"""
        try:
            if COMMAND_QUEUE_FILE.exists():
                with open(COMMAND_QUEUE_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading command queue: {e}")
        return []
    
    def get_pending_commands(self) -> List[dict]:
        """Get commands that haven't been processed yet"""
        all_commands = self.load_command_queue()
        pending = []
        
        for command in all_commands:
            command_id = self.get_command_id(command)
            if command_id not in self.processed_commands:
                pending.append(command)
        
        return pending
    
    def can_run_command(self) -> bool:
        """Check if we can run a new command (not exceeding concurrent limit)"""
        # Clean up finished processes
        for cmd_id in list(self.running_processes.keys()):
            process = self.running_processes[cmd_id]
            if process.poll() is not None:  # Process finished
                del self.running_processes[cmd_id]
                logger.info(f"Command {cmd_id} finished with return code {process.returncode}")
        
        return len(self.running_processes) < MAX_CONCURRENT_PROCESSES
    
    def execute_command(self, command_entry: dict):
        """Execute a command via Claude Code"""
        command_id = self.get_command_id(command_entry)
        command_text = command_entry['command']
        
        try:
            logger.info(f"Executing command {command_id}: {command_text}")
            
            # Construct Claude Code command
            claude_cmd = [
                CLAUDE_CODE_COMMAND,
                "-p",  # Non-interactive mode
                command_text
            ]
            
            # Set up environment
            env = os.environ.copy()
            
            # Execute command
            process = subprocess.Popen(
                claude_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                cwd=Path.home()  # Default to home directory
            )
            
            # Store running process
            self.running_processes[command_id] = process
            
            # Mark as processed immediately to avoid duplicates
            self.processed_commands.add(command_id)
            self.save_processed_commands()
            
            # Log command execution
            logger.info(f"Started Claude Code for command {command_id}")
            
        except FileNotFoundError:
            logger.error(f"Claude Code command not found: {CLAUDE_CODE_COMMAND}")
            logger.error("Make sure Claude Code is installed and in your PATH")
        except Exception as e:
            logger.error(f"Error executing command {command_id}: {e}")
    
    def check_claude_code_available(self) -> bool:
        """Check if Claude Code is available in the system"""
        try:
            result = subprocess.run(
                [CLAUDE_CODE_COMMAND, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def run_monitor(self):
        """Main monitoring loop"""
        logger.info("Starting Claude Code command monitor")
        
        # Check if Claude Code is available
        if not self.check_claude_code_available():
            logger.error(f"Claude Code not available at: {CLAUDE_CODE_COMMAND}")
            logger.error("Please install Claude Code or update the CLAUDE_CODE_COMMAND path")
            return
        
        logger.info(f"Claude Code is available at: {CLAUDE_CODE_COMMAND}")
        logger.info(f"Monitoring queue file: {COMMAND_QUEUE_FILE}")
        logger.info(f"Poll interval: {POLL_INTERVAL} seconds")
        
        try:
            while True:
                # Get pending commands
                pending_commands = self.get_pending_commands()
                
                # Execute commands if we have capacity
                for command in pending_commands:
                    if self.can_run_command():
                        self.execute_command(command)
                    else:
                        logger.info("Max concurrent processes reached, waiting...")
                        break
                
                # Wait before next poll
                time.sleep(POLL_INTERVAL)
                
        except KeyboardInterrupt:
            logger.info("Shutting down monitor...")
            
            # Wait for running processes to complete
            for cmd_id, process in self.running_processes.items():
                logger.info(f"Waiting for command {cmd_id} to complete...")
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    logger.warning(f"Command {cmd_id} timed out, terminating...")
                    process.terminate()
                    
        except Exception as e:
            logger.error(f"Monitor error: {e}")
        
        logger.info("Monitor stopped")

def main():
    """Main function"""
    monitor = ClaudeMonitor()
    monitor.run_monitor()

if __name__ == "__main__":
    main()