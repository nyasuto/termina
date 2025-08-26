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

Termina is a macOS desktop application that enables voice input for any application. It's a menu bar application that records audio, transcribes it using OpenAI Whisper API or local Whisper models, and pastes the transcribed text into the currently active application via AppleScript.

**Current Status**: Fully implemented with core functionality complete. Features include multiple speech providers, configurable recording, hotkey support, and model management.

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
- **Speech Recognition**: 
  - OpenAI Whisper API via `openai` library
  - Local Whisper via `openai-whisper` library
- **System Integration**: AppleScript via `osascript`
- **Environment Management**: `python-dotenv`
- **Global Hotkeys**: `pynput`
- **HTTP Requests**: `requests` (for model downloading)
- **Audio Processing**: `numpy`, `scipy`

## Development Setup (uv)

```bash
# Install uv (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync dependencies
uv sync

# Create environment configuration
echo "OPENAI_API_KEY=your-openai-api-key-here" > .env.local
echo "SPEECH_PROVIDER=openai" >> .env.local

# Run the application
uv run python termina.py
```

### Environment Configuration

Create a `.env.local` file in the project root:

```bash
# OpenAI Whisper API (recommended for best accuracy)
OPENAI_API_KEY=your-openai-api-key-here
SPEECH_PROVIDER=openai

# OR use local Whisper (offline, no API key needed)
# SPEECH_PROVIDER=whisper_cpp
```

## Architecture

The application follows this workflow:
1. Menu bar interface with microphone icon (🎤)
2. User-controlled audio recording (start/stop manually or via ⌘+Shift+V hotkey)
3. Save audio to temporary `.wav` file with 16kHz sampling rate
4. Send audio to configured speech provider for transcription:
   - **OpenAI Provider**: API call to Whisper API with Japanese language setting
   - **Local Whisper Provider**: Uses openai-whisper library with configurable model sizes
5. Paste transcribed text into currently active application via AppleScript

### Key Components

- **`termina.py`**: Main application entry point and menu bar interface
- **`speech_providers.py`**: Speech recognition provider implementations
  - `OpenAIProvider`: OpenAI Whisper API integration
  - `WhisperCppProvider`: Local openai-whisper integration
  - `SpeechProviderFactory`: Provider selection and management
- **`whisper_models.py`**: Local Whisper model management and downloading

## Key Implementation Notes

- **macOS-specific**: Uses `rumps` for menu bar UI and AppleScript for text input
- **Permissions required**: 
  - Microphone access for audio recording
  - Accessibility permissions for global hotkeys and text pasting
- **Main entry point**: `termina.py`
- **Temporary files**: Audio stored as temporary `.wav` files during processing
- **Speech providers**: Supports both online (OpenAI API) and offline (local Whisper) transcription
- **Language optimization**: Configured for Japanese language recognition
- **Audio processing**: 16kHz sampling rate, noise reduction, and audio normalization

## Dependencies

See `pyproject.toml` for the complete list. Key dependencies include:

```
rumps>=0.4.0                 # macOS menu bar UI
sounddevice>=0.4.6           # Audio recording
scipy>=1.11.0                # Audio processing
numpy>=1.21.0                # Array operations
openai>=1.0.0                # OpenAI Whisper API
python-dotenv>=1.0.0         # Environment variables
pynput>=1.7.6                # Global hotkeys
openai-whisper>=20231117     # Local Whisper (optional)
requests>=2.25.0             # HTTP requests for model downloading
```

## Development Tools & CI/CD

The project includes:
- **GitHub Actions**: CI/CD pipeline with testing, linting, formatting, and security checks
- **Code Quality**: Black formatter, mypy type checking, flake8 linting
- **Security**: Bandit security scanner, safety dependency vulnerability checks
- **Dependabot**: Automated dependency updates

## Testing & Quality

```bash
# Run type checking
python3 -m mypy .

# Format code
python3 -m black .

# Security scan
python3 -m bandit -r . --severity-level medium

# Lint code
flake8 . --max-line-length=88
```

## Development Guidelines

### Code Style
- Follow PEP 8 Python style guide
- Use Black formatter for consistent formatting
- Add type hints for all functions and methods
- Maximum line length: 88 characters
- Use meaningful variable and function names

### Error Handling
- Always handle exceptions gracefully
- Provide user-friendly error messages via rumps notifications
- Log errors for debugging purposes
- Never expose sensitive information in error messages

### Audio Processing Best Practices
- Always use 16kHz sampling rate for Whisper compatibility
- Apply noise reduction and normalization for better transcription accuracy
- Clean up temporary audio files after processing
- Handle recording interruptions gracefully

### Security Considerations
- Never commit API keys or sensitive configuration
- Use `.env.local` for local development secrets
- Validate all user inputs
- Implement timeout for network requests
- Encrypt temporary audio files if needed

### Testing Strategy
- Write unit tests for each speech provider
- Test error conditions and edge cases
- Mock external API calls in tests
- Test on different macOS versions
- Verify microphone and accessibility permissions

## Troubleshooting

### Common Development Issues

1. **Import errors**: Ensure virtual environment is activated
2. **Permission errors**: Grant microphone and accessibility permissions in System Preferences
3. **API failures**: Check API key validity and network connectivity
4. **Audio issues**: Verify microphone access and sample rate compatibility
5. **Hotkey conflicts**: Check for conflicting system shortcuts

### Debugging

Enable debug mode by setting environment variable:
```bash
export DEBUG=1
python termina.py
```

## Contributing

When contributing to this project:

1. Run all quality checks before submitting PR
2. Update documentation for new features
3. Test on clean macOS environment
4. Follow the established code style

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

- ✅ Global hotkey support (implemented: ⌘+Shift+V)
- ✅ Offline Whisper support (implemented via openai-whisper)
- 🔄 Dynamic recording duration with silence detection
- 🔄 Command confirmation prompts
- 🔄 Custom hotkey configuration
- 🔄 Recording history and management
- 🔄 Multiple language support beyond Japanese
- 🔄 Plugin system for custom post-processing
- 🔄 Integration with popular text editors and IDEs
