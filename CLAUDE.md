# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

WhisperTerm is a macOS desktop application that enables voice control of Terminal commands. It's a menu bar application that records audio, transcribes it using OpenAI Whisper API, and executes the transcribed text as Terminal commands via AppleScript.

**Current Status**: Early development stage - comprehensive documentation exists but implementation is not yet started.

## Technology Stack

- **Language**: Python 3.9+
- **GUI Framework**: `rumps` (macOS menu bar applications)
- **Audio**: `sounddevice`, `scipy.io.wavfile`
- **Speech Recognition**: OpenAI Whisper API via `openai` library
- **System Integration**: AppleScript via `osascript`

## Development Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies (when requirements.txt exists)
pip install -r requirements.txt

# Set OpenAI API key
export OPENAI_API_KEY="your-key-here"

# Run the application (when implemented)
python whisper_menu_app.py
```

## Architecture

The application follows this workflow:
1. Menu bar interface with microphone icon
2. 5-second audio recording on user action
3. Save audio to temporary `temp.wav` file
4. Send audio to OpenAI Whisper API for transcription
5. Execute transcribed text as Terminal commands via AppleScript

## Key Implementation Notes

- **macOS-specific**: Uses `rumps` for menu bar UI and AppleScript for Terminal integration
- **Permissions required**: Microphone access and potentially accessibility permissions
- **Main entry point**: `whisper_menu_app.py` (to be implemented)
- **Temporary files**: Audio stored as `temp.wav` during processing
- **API dependency**: Requires internet connection and OpenAI API key

## Planned Dependencies

```
rumps
sounddevice
scipy
openai
```

## Future Enhancements

- Global hotkey support (requires accessibility permissions)
- Dynamic recording duration with silence detection
- Command confirmation prompts
- Offline Whisper support via whisper.cpp