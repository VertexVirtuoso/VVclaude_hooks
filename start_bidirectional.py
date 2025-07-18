#!/usr/bin/env python3
"""
Startup script for bidirectional Claude Code communication.
Starts both the Discord bot and the command monitor.
"""

import os
import sys
import subprocess
import signal
import logging
from pathlib import Path
from typing import List

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BidirectionalStarter:
    def __init__(self):
        self.processes: List[subprocess.Popen] = []
        self.script_dir = Path(__file__).parent
        
    def check_requirements(self) -> bool:
        """Check if all requirements are met"""
        # Check for .env file
        env_file = Path.home() / ".env"
        if not env_file.exists():
            logger.error(f"Environment file not found: {env_file}")
            return False
        
        # Check for required environment variables
        required_vars = ['DISCORD_WEBHOOK', 'DISCORD_BOT_TOKEN', 'AUTHORIZED_USER_ID']
        missing_vars = []
        
        try:
            with open(env_file, 'r') as f:
                env_content = f.read()
                for var in required_vars:
                    if f"{var}=YOUR_" in env_content or f"{var}=" not in env_content:
                        missing_vars.append(var)
        except Exception as e:
            logger.error(f"Error reading .env file: {e}")
            return False
        
        if missing_vars:
            logger.error(f"Missing or unconfigured environment variables: {missing_vars}")
            logger.error("Please update your .env file with the required values")
            return False
        
        # Check for script files
        required_scripts = ['discord_bot.py', 'claude_monitor.py']
        for script in required_scripts:
            script_path = self.script_dir / script
            if not script_path.exists():
                logger.error(f"Required script not found: {script_path}")
                return False
        
        return True
    
    def start_process(self, script_name: str, description: str) -> subprocess.Popen:
        """Start a background process"""
        script_path = self.script_dir / script_name
        
        try:
            # Make script executable
            os.chmod(script_path, 0o755)
            
            # Start process
            process = subprocess.Popen(
                [sys.executable, str(script_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            logger.info(f"Started {description} (PID: {process.pid})")
            self.processes.append(process)
            return process
            
        except Exception as e:
            logger.error(f"Error starting {description}: {e}")
            raise
    
    def check_processes(self):
        """Check if processes are still running"""
        for i, process in enumerate(self.processes):
            if process.poll() is not None:
                logger.warning(f"Process {i} terminated with code {process.returncode}")
                # Get stderr output
                _, stderr = process.communicate()
                if stderr:
                    logger.error(f"Process {i} stderr: {stderr}")
    
    def stop_all(self):
        """Stop all processes"""
        logger.info("Stopping all processes...")
        
        for i, process in enumerate(self.processes):
            if process.poll() is None:  # Still running
                logger.info(f"Terminating process {i} (PID: {process.pid})")
                process.terminate()
                
                # Wait for graceful shutdown
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    logger.warning(f"Process {i} didn't terminate gracefully, killing...")
                    process.kill()
        
        logger.info("All processes stopped")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.stop_all()
        sys.exit(0)
    
    def run(self):
        """Main run method"""
        logger.info("Starting bidirectional Claude Code communication system")
        
        # Check requirements
        if not self.check_requirements():
            logger.error("Requirements not met, exiting")
            return 1
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        try:
            # Start Discord bot
            self.start_process('discord_bot.py', 'Discord bot')
            
            # Start command monitor
            self.start_process('claude_monitor.py', 'Command monitor')
            
            logger.info("All processes started successfully")
            logger.info("System is ready for bidirectional communication")
            logger.info("Press Ctrl+C to stop all processes")
            
            # Monitor processes
            while True:
                self.check_processes()
                
                # Check if all processes are still running
                running_count = sum(1 for p in self.processes if p.poll() is None)
                if running_count == 0:
                    logger.error("All processes have terminated")
                    break
                
                # Wait before next check
                import time
                time.sleep(5)
                
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
        finally:
            self.stop_all()
        
        return 0

def main():
    """Main function"""
    starter = BidirectionalStarter()
    return starter.run()

if __name__ == "__main__":
    sys.exit(main())