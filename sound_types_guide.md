# Claude Code Sound Types & Hook Guide

## Available Hook Types

Claude Code supports several hook types that trigger at different events:

### 1. **Task Completion Hook** (what you currently have)
- **Script**: `notification.py`
- **Triggered**: When Claude finishes implementing/completing a task
- **Current Sound**: `success` (upgrade_complete.wav)

### 2. **Session Stop Hook**
- **Script**: `stop.py` (identical to notification.py)
- **Triggered**: When Claude Code session ends
- **Suggested Sound**: `session_end`

### 3. **Error Hook** (potential)
- **Triggered**: When Claude encounters errors
- **Suggested Sound**: `error`

### 4. **Research Complete Hook** (custom implementation)
- **Triggered**: When Claude finishes research/analysis tasks
- **Suggested Sound**: `research_complete`

## Sound Categories in Your Configuration

Based on your `sound_config.json`, you can customize these sound types:

### Built-in Categories:
1. **success** - Task completion, successful operations
2. **error** - Failures, exceptions, critical issues
3. **warning** - Non-critical issues, warnings

### Suggested Custom Categories:
4. **research_complete** - When Claude finishes analyzing/researching
5. **session_start** - When Claude Code session begins
6. **session_end** - When Claude Code session ends
7. **coding_start** - When Claude begins implementing code
8. **testing_complete** - When tests finish running
9. **git_commit** - When commits are made
10. **build_complete** - When build processes finish

## Current Sound Setup

Your current configuration uses:
- **Primary**: `/home/charlie/.claude/hooks/audio/upgrade_complete.wav`
- **Fallbacks**: System sounds (paplay, aplay, speaker-test, beep)

## Customization Options

### 1. Add New Sound Categories
```json
{
  "sounds": {
    "research_complete": {
      "linux": [
        {
          "command": ["paplay", "/home/charlie/.claude/hooks/audio/research_done.wav"],
          "description": "Research completion sound"
        }
      ]
    },
    "session_start": {
      "linux": [
        {
          "command": ["paplay", "/home/charlie/.claude/hooks/audio/session_start.wav"],
          "description": "Session start sound"
        }
      ]
    }
  }
}
```

### 2. Different Sounds for Different Contexts
- **Quick tasks**: Short beep
- **Complex implementations**: Longer, more elaborate sound
- **Research tasks**: Different tone/melody
- **Error conditions**: Alert-style sounds

## Hook Implementation Strategy

### Current: Single Hook (notification.py)
- All completions use same sound
- No differentiation between task types

### Enhanced: Context-Aware Hooks
- Parse Claude's response/context
- Choose sound based on task type
- Different sounds for different completion types

## Recommended Next Steps

1. **Add more audio files** to `/home/charlie/.claude/hooks/audio/`
2. **Enhance notification.py** to detect task type from input
3. **Create specialized hooks** for different events
4. **Configure Claude Code** to use multiple hook types

Would you like me to:
1. Help you set up additional sound categories?
2. Enhance the notification script to use different sounds based on task type?
3. Show you how to configure multiple hook types in Claude Code?