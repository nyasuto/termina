"""Basic smoke tests for Termina modules"""


def test_import_modules():
    """Test that all main modules can be imported"""
    import ffmpeg_processor
    import speech_providers
    import termina  # This will test if all imports work
    import whisper_models

    assert ffmpeg_processor is not None
    assert speech_providers is not None
    assert whisper_models is not None
    assert termina is not None


def test_ffmpeg_processor_creation():
    """Test FFmpeg processor can be created"""
    from ffmpeg_processor import FFmpegAudioProcessor, get_processor

    processor = FFmpegAudioProcessor()
    assert processor is not None

    # Test singleton
    processor2 = get_processor()
    assert processor2 is not None


def test_speech_provider_factory():
    """Test speech provider factory basic functionality"""
    from speech_providers import SpeechProviderFactory

    # Test getting available providers (should not crash)
    providers = SpeechProviderFactory.get_available_providers()
    assert isinstance(providers, list)

    # Test getting OpenAI provider (may be None if not available)
    # Provider availability depends on environment, just test it doesn't crash
    SpeechProviderFactory.get_provider("openai")

    # Test invalid provider returns None
    invalid_provider = SpeechProviderFactory.get_provider("invalid")
    assert invalid_provider is None


def test_whisper_model_manager_creation():
    """Test whisper model manager can be created"""
    from whisper_models import WhisperModelManager

    manager = WhisperModelManager()
    assert manager is not None
    assert hasattr(manager, "MODELS")
    assert "tiny" in manager.MODELS
    assert "large" in manager.MODELS


def test_project_structure():
    """Test project structure and key components exist"""
    from pathlib import Path

    # Test key files exist
    project_root = Path(__file__).parent.parent
    assert (project_root / "pyproject.toml").exists()
    assert (project_root / "README.md").exists()
    assert (project_root / "Makefile").exists()
    assert (project_root / ".python-version").exists()
    assert (project_root / "uv.lock").exists()


def test_configuration_files():
    """Test configuration is properly set up"""
    from pathlib import Path

    import toml

    project_root = Path(__file__).parent.parent
    pyproject_path = project_root / "pyproject.toml"

    config = toml.load(pyproject_path)

    # Test project metadata
    assert "project" in config
    assert config["project"]["name"] == "termina"
    assert "dependencies" in config["project"]

    # Test tool configuration
    assert "tool" in config
    assert "ruff" in config["tool"]
    assert "pytest" in config["tool"]
