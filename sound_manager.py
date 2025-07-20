#!/usr/bin/env python3
"""
Sound manager for Claude Code hooks.
Handles sound configuration and playback with customizable options.
"""

import os
import json
import platform
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class SoundManager:
    def __init__(self, config_file: str = None):
        """Initialize sound manager with configuration"""
        self.config_file = config_file or Path(__file__).parent / "sound_config.json"
        self.config = self.load_config()
        self.system = platform.system()
        
    def load_config(self) -> Dict:
        """Load sound configuration from JSON file"""
        try:
            if Path(self.config_file).exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    return config
            else:
                print(f"Warning: Sound config file not found: {self.config_file}")
                return self.get_default_config()
        except Exception as e:
            print(f"Error loading sound config: {e}")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict:
        """Get default sound configuration"""
        return {
            "sound_settings": {
                "enabled": True,
                "volume": 80,
                "notification_type": "system_default"
            },
            "sounds": {
                "success": {
                    "linux": [{"command": ["echo", "-e", "\\a"], "description": "Terminal bell"}],
                    "macos": [{"command": ["afplay", "/System/Library/Sounds/Hero.aiff"], "description": "Hero sound"}],
                    "windows": [{"command": ["powershell", "-c", "[System.Media.SystemSounds]::Asterisk.Play()"], "description": "Windows Asterisk"}]
                }
            },
            "custom_sounds": {"enabled": False}
        }
    
    def is_sound_enabled(self) -> bool:
        """Check if sound is enabled"""
        return self.config.get("sound_settings", {}).get("enabled", True)
    
    def get_sound_commands(self, sound_type: str = "success") -> List[Dict]:
        """Get available sound commands for the current system and sound type"""
        if not self.is_sound_enabled():
            return []
        
        system_key = {
            "Linux": "linux",
            "Darwin": "macos", 
            "Windows": "windows"
        }.get(self.system, "linux")
        
        sounds = self.config.get("sounds", {})
        sound_config = sounds.get(sound_type, sounds.get("success", {}))
        
        return sound_config.get(system_key, [])
    
    def play_sound(self, sound_type: str = "success", verbose: bool = True) -> bool:
        """Play a sound of the specified type"""
        if not self.is_sound_enabled():
            if verbose:
                print("🔇 Sound is disabled in configuration")
            return True
        
        # Check for custom sounds first
        if self.try_custom_sound(sound_type, verbose):
            return True
        
        # Fall back to system sounds
        return self.try_system_sounds(sound_type, verbose)
    
    def try_custom_sound(self, sound_type: str, verbose: bool = True) -> bool:
        """Try to play custom sound if enabled"""
        custom_config = self.config.get("custom_sounds", {})
        if not custom_config.get("enabled", False):
            return False
        
        sound_dir = Path(custom_config.get("sound_directory", "~/.claude/hooks/sounds/")).expanduser()
        examples = custom_config.get("examples", {})
        
        if sound_type in examples:
            sound_file = sound_dir / examples[sound_type]
            if sound_file.exists():
                return self.play_audio_file(sound_file, verbose)
        
        # Try common naming patterns
        formats = custom_config.get("formats", [".wav", ".mp3", ".ogg"])
        for format_ext in formats:
            sound_file = sound_dir / f"{sound_type}{format_ext}"
            if sound_file.exists():
                return self.play_audio_file(sound_file, verbose)
        
        return False
    
    def play_audio_file(self, file_path: Path, verbose: bool = True) -> bool:
        """Play an audio file using appropriate system command"""
        try:
            if self.system == "Linux":
                # Try multiple Linux audio players
                players = [
                    ["paplay", str(file_path)],
                    ["aplay", str(file_path)],
                    ["mpg123", str(file_path)],
                    ["ogg123", str(file_path)]
                ]
                
                for player in players:
                    try:
                        subprocess.run(player, check=True, capture_output=True, timeout=5)
                        if verbose:
                            print(f"🔊 Played custom sound: {file_path.name}")
                        return True
                    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                        continue
                        
            elif self.system == "Darwin":  # macOS
                subprocess.run(["afplay", str(file_path)], check=True, timeout=5)
                if verbose:
                    print(f"🔊 Played custom sound: {file_path.name}")
                return True
                
            elif self.system == "Windows":
                # Use PowerShell to play audio
                cmd = f'(New-Object Media.SoundPlayer "{file_path}").PlaySync()'
                subprocess.run(["powershell", "-c", cmd], check=True, timeout=5)
                if verbose:
                    print(f"🔊 Played custom sound: {file_path.name}")
                return True
                
        except Exception as e:
            if verbose:
                print(f"❌ Error playing custom sound {file_path}: {e}")
        
        return False
    
    def try_system_sounds(self, sound_type: str, verbose: bool = True) -> bool:
        """Try to play system sounds"""
        import random
        
        sound_commands = self.get_sound_commands(sound_type)
        
        if not sound_commands:
            if verbose:
                print(f"⚠️  No sound commands available for {sound_type} on {self.system}")
            return False
        
        # For completion sounds with multiple options, randomly select one
        if len(sound_commands) > 1 and sound_type in ["implementation_complete", "thinking", "error_found"]:
            sound_commands = [random.choice(sound_commands)]
        
        for sound_config in sound_commands:
            try:
                command = sound_config["command"]
                description = sound_config.get("description", "Unknown sound")
                
                subprocess.run(command, check=True, capture_output=True, timeout=5)
                
                if verbose:
                    print(f"🔊 Played sound: {description}")
                return True
                
            except subprocess.CalledProcessError:
                continue
            except FileNotFoundError:
                continue
            except subprocess.TimeoutExpired:
                if verbose:
                    print(f"⏰ Sound command timed out: {description}")
                continue
            except Exception as e:
                if verbose:
                    print(f"❌ Error playing sound '{description}': {e}")
                continue
        
        if verbose:
            print("❌ No sound commands worked on this system")
        return False
    
    def test_all_sounds(self):
        """Test all available sounds"""
        print("🎵 Testing all available sounds...")
        print("=" * 40)
        
        for sound_type in ["success", "error", "warning"]:
            print(f"\n🎯 Testing {sound_type} sounds:")
            sound_commands = self.get_sound_commands(sound_type)
            
            if not sound_commands:
                print(f"   No sounds configured for {sound_type}")
                continue
            
            for i, sound_config in enumerate(sound_commands, 1):
                description = sound_config.get("description", "Unknown")
                print(f"   {i}. Testing: {description}")
                
                try:
                    command = sound_config["command"]
                    result = subprocess.run(command, check=True, capture_output=True, timeout=3)
                    print(f"      ✅ Success")
                except subprocess.CalledProcessError as e:
                    print(f"      ❌ Failed (exit code {e.returncode})")
                except FileNotFoundError:
                    print(f"      ❌ Command not found")
                except subprocess.TimeoutExpired:
                    print(f"      ⏰ Timeout")
                except Exception as e:
                    print(f"      ❌ Error: {e}")
                
                # Small delay between sounds
                import time
                time.sleep(0.5)
    
    def get_config_summary(self) -> str:
        """Get a summary of current sound configuration"""
        enabled = "✅ Enabled" if self.is_sound_enabled() else "❌ Disabled"
        system = self.system
        
        success_sounds = len(self.get_sound_commands("success"))
        error_sounds = len(self.get_sound_commands("error"))
        warning_sounds = len(self.get_sound_commands("warning"))
        
        custom_enabled = self.config.get("custom_sounds", {}).get("enabled", False)
        custom_status = "✅ Enabled" if custom_enabled else "❌ Disabled"
        
        return f"""
🎵 Sound Configuration Summary
{'=' * 35}
Status: {enabled}
System: {system}
Available sounds:
  - Success: {success_sounds} commands
  - Error: {error_sounds} commands  
  - Warning: {warning_sounds} commands
Custom sounds: {custom_status}
Config file: {self.config_file}
"""

def main():
    """Test the sound manager"""
    manager = SoundManager()
    
    print(manager.get_config_summary())
    
    # Test playing a sound
    print("\n🎯 Testing success sound:")
    manager.play_sound("success")
    
    # Optionally test all sounds
    import sys
    if "--test-all" in sys.argv:
        manager.test_all_sounds()

if __name__ == "__main__":
    main()