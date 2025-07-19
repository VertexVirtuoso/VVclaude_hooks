#!/usr/bin/env python3
"""
Sound configuration helper for Claude Code hooks.
Allows testing and configuring notification sounds.
"""

import sys
import json
from pathlib import Path
from sound_manager import SoundManager

def show_current_config(manager):
    """Show current sound configuration"""
    print(manager.get_config_summary())

def test_sounds(manager):
    """Test all available sounds"""
    print("🎵 Testing notification sounds...")
    print("=" * 40)
    
    sound_types = ["success", "warning", "error"]
    
    for sound_type in sound_types:
        print(f"\n🎯 Testing {sound_type} sound:")
        input(f"   Press Enter to play {sound_type} sound...")
        success = manager.play_sound(sound_type)
        if not success:
            print(f"   ❌ Failed to play {sound_type} sound")
        print("")

def toggle_sounds(manager):
    """Toggle sound enable/disable"""
    current_enabled = manager.is_sound_enabled()
    new_enabled = not current_enabled
    
    # Update config
    manager.config["sound_settings"]["enabled"] = new_enabled
    
    # Save config
    try:
        with open(manager.config_file, 'w') as f:
            json.dump(manager.config, f, indent=2)
        
        status = "enabled" if new_enabled else "disabled"
        print(f"✅ Sounds {status} successfully!")
        
    except Exception as e:
        print(f"❌ Error saving configuration: {e}")

def show_available_sounds(manager):
    """Show all available sound commands"""
    print("🎵 Available Sound Commands")
    print("=" * 40)
    
    system = manager.system
    print(f"System: {system}")
    
    for sound_type in ["success", "warning", "error"]:
        print(f"\n🎯 {sound_type.capitalize()} sounds:")
        commands = manager.get_sound_commands(sound_type)
        
        if not commands:
            print("   No sounds configured")
            continue
            
        for i, cmd_config in enumerate(commands, 1):
            command = " ".join(cmd_config["command"])
            description = cmd_config.get("description", "No description")
            print(f"   {i}. {description}")
            print(f"      Command: {command}")

def edit_config_file(manager):
    """Open config file for editing"""
    config_file = manager.config_file
    print(f"📝 Configuration file: {config_file}")
    print()
    print("To edit the configuration:")
    print(f"   nano {config_file}")
    print("   or")
    print(f"   code {config_file}")
    print()
    print("After editing, restart your hooks or run this script again to test.")

def create_custom_sounds_directory():
    """Create directory for custom sounds"""
    sounds_dir = Path.home() / ".claude" / "hooks" / "sounds"
    sounds_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Created custom sounds directory: {sounds_dir}")
    print()
    print("To use custom sounds:")
    print(f"1. Place sound files in: {sounds_dir}")
    print("2. Name them: success.wav, warning.wav, error.wav")
    print("3. Update sound_config.json to enable custom sounds")
    print("4. Set 'custom_sounds.enabled' to true")

def interactive_menu():
    """Show interactive menu"""
    manager = SoundManager()
    
    while True:
        print("\n🎵 Claude Code Sound Configuration")
        print("=" * 40)
        print("1. Show current configuration")
        print("2. Test all sounds")
        print("3. Show available sound commands")
        print("4. Toggle sounds on/off")
        print("5. Edit configuration file")
        print("6. Create custom sounds directory")
        print("7. Reload configuration")
        print("0. Exit")
        print()
        
        try:
            choice = input("Select option (0-7): ").strip()
            
            if choice == "0":
                print("👋 Goodbye!")
                break
            elif choice == "1":
                show_current_config(manager)
            elif choice == "2":
                test_sounds(manager)
            elif choice == "3":
                show_available_sounds(manager)
            elif choice == "4":
                toggle_sounds(manager)
            elif choice == "5":
                edit_config_file(manager)
            elif choice == "6":
                create_custom_sounds_directory()
            elif choice == "7":
                manager = SoundManager()  # Reload
                print("✅ Configuration reloaded!")
            else:
                print("❌ Invalid option. Please choose 0-7.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Main function"""
    if len(sys.argv) > 1:
        # Command line mode
        command = sys.argv[1].lower()
        manager = SoundManager()
        
        if command == "test":
            print("🎯 Testing success sound:")
            manager.play_sound("success")
        elif command == "test-all":
            manager.test_all_sounds()
        elif command == "config":
            show_current_config(manager)
        elif command == "toggle":
            toggle_sounds(manager)
        elif command == "sounds":
            show_available_sounds(manager)
        else:
            print("Usage: python3 configure_sounds.py [test|test-all|config|toggle|sounds]")
            print("   Or run without arguments for interactive mode")
    else:
        # Interactive mode
        interactive_menu()

if __name__ == "__main__":
    main()