# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🚨 MANDATORY INSTRUCTIONS FOR CLAUDE CODE

### Primary Rule: NO DIRECT COMMITS TO MAIN

**BEFORE EVERY COMMIT OPERATION:**
1. Run `git status` or `git branch` to check current branch
2. If on `main` branch: STOP and create new feature branch first
3. NEVER run `git commit` while on main branch
4. Always use feature branches for all changes

**This is a HARD REQUIREMENT and must be followed without exception.**

## Project Overview

WhisperTerm is a macOS desktop application that enables voice control of Terminal commands. It's a menu bar application that records audio, transcribes it using OpenAI Whisper API, and executes the transcribed text as Terminal commands via AppleScript.

**Current Status**: Early development stage - comprehensive documentation exists but implementation is not yet started.

## ⚠️ CRITICAL: Branch Protection Rules

**NEVER COMMIT DIRECTLY TO MAIN BRANCH**

### Mandatory Workflow for All Commits

1. **Before ANY commit**: Check current branch with `git branch` or `git status`
2. **If on main branch**: ALWAYS create a new feature branch first
3. **Only commit to feature branches**: Never commit directly to main
4. **Use Pull Requests**: All changes to main must go through PR review

### Commit Command Behavior

When user says "commit" or requests a commit:

1. **Check current branch first**: `git branch` or `git status`
2. **If on main branch**: 
   - Automatically create new feature branch with descriptive name
   - Switch to the new branch
   - Then perform the commit
3. **If on feature branch**: Proceed with commit normally

### Branch Naming Convention

Use descriptive branch names with prefixes:
- `feat/`: New features (`feat/add-hotkey-support`)
- `fix/`: Bug fixes (`fix/audio-processing-error`)
- `docs/`: Documentation updates (`docs/update-readme`)
- `refactor/`: Code refactoring (`refactor/speech-providers`)
- `test/`: Test additions (`test/add-unit-tests`)

### Example Safe Commit Flow

```bash
# Check current branch
git status

# If on main, create feature branch
git checkout -b feat/new-feature

# Make changes and commit
git add .
git commit -m "Add new feature"

# Push and create PR
git push -u origin feat/new-feature
gh pr create
```

**This rule prevents accidental commits to main and maintains clean git history.**

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

## Git Workflow for Claude Code

### Commit Safety Checklist

Before any commit operation, Claude Code must:

✅ Check current branch: `git status`  
✅ If on main: Create feature branch first  
✅ Use descriptive branch names with prefixes  
✅ Never commit directly to main  
✅ Always use Pull Requests for main branch changes  

### Implementation Guidelines

When implementing new features or fixes:

1. **Check branch status first**: Always verify current branch
2. **Create appropriate branch**: Use feat/, fix/, docs/, etc. prefixes
3. **Make focused commits**: Single purpose per commit
4. **Write clear commit messages**: Explain what and why
5. **Create PR for review**: All main branch changes via PR

## Future Enhancements

- Global hotkey support (requires accessibility permissions)
- Dynamic recording duration with silence detection
- Command confirmation prompts
- Offline Whisper support via whisper.cpp