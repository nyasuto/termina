# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Termina is a macOS desktop application that enables voice input for any application. It's a menu bar application that records audio, transcribes it using OpenAI Whisper API or local Whisper models, and pastes the transcribed text into the currently active application via AppleScript.

**Current Status**: Fully implemented with core functionality complete. Features include multiple speech providers, configurable recording, hotkey support, and model management.

## Commit rule
if you are in main branch, create new branch then commit the changes into new branch
do not commit into main branch directly

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

## Development Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment configuration
echo "OPENAI_API_KEY=your-openai-api-key-here" > .env.local
echo "SPEECH_PROVIDER=openai" >> .env.local

# Run the application
python termina.py
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
2. User-controlled audio recording (start/stop manually or via ⌘+H hotkey)
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

See `requirements.txt` for the complete list. Key dependencies include:

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

1. Create a feature branch from main
2. Follow the branching strategy defined in commit rules
3. Run all quality checks before submitting PR
4. Update documentation for new features
5. Test on clean macOS environment
6. Follow the established code style

## Future Enhancements

- ✅ Global hotkey support (implemented: ⌘+H)
- ✅ Offline Whisper support (implemented via openai-whisper)
- 🔄 Dynamic recording duration with silence detection
- 🔄 Command confirmation prompts
- 🔄 Custom hotkey configuration
- 🔄 Recording history and management
- 🔄 Multiple language support beyond Japanese
- 🔄 Plugin system for custom post-processing
- 🔄 Integration with popular text editors and IDEs