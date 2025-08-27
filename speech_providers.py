#!/usr/bin/env python3
"""
Speech Recognition Providers for Termina
Abstracts different speech recognition backends (OpenAI API, FFmpeg + whisper.cpp)
"""

import os
import subprocess
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

from ffmpeg_processor import get_processor


class SpeechProvider(ABC):
    """Abstract base class for speech recognition providers"""

    @abstractmethod
    def transcribe(self, audio_path: str) -> Optional[str]:
        """
        Transcribe audio file to text

        Args:
            audio_path: Path to the audio file

        Returns:
            Transcribed text or None if transcription failed
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the provider is available and properly configured

        Returns:
            True if provider can be used, False otherwise
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of the provider"""
        pass

    @property
    @abstractmethod
    def requires_internet(self) -> bool:
        """Whether this provider requires internet connection"""
        pass


class OpenAIProvider(SpeechProvider):
    """OpenAI Whisper API provider"""

    def __init__(self):
        load_dotenv(".env.local")
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    def transcribe(self, audio_path: str) -> Optional[str]:
        """Transcribe audio using OpenAI Whisper API"""
        if not self.is_available():
            print("OpenAI provider not available")
            return None

        try:
            print(f"Starting OpenAI transcription for file: {audio_path}")

            # Apply FFmpeg noise reduction if available
            processor = get_processor()
            if processor.ffmpeg_available and processor.noise_reduction_enabled:
                print("Applying FFmpeg noise reduction before transcription...")
                audio_path = processor.process_audio(audio_path)

            # Check if file exists and get its size
            if not os.path.exists(audio_path):
                print(f"Error: Audio file does not exist: {audio_path}")
                return None

            file_size = os.path.getsize(audio_path)
            print(f"Audio file size: {file_size} bytes")

            if file_size == 0:
                print("Error: Audio file is empty")
                return None

            with open(audio_path, "rb") as audio_file:
                print("Sending request to OpenAI Whisper API...")
                transcription = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="ja",  # Japanese language setting
                )

                result_text = transcription.text.strip()
                print(f"OpenAI transcription successful: '{result_text}'")
                return result_text

        except Exception as e:
            print(f"OpenAI transcription error: {e}")
            import traceback

            traceback.print_exc()
            return None

    def is_available(self) -> bool:
        """Check if OpenAI API key is configured"""
        return self.api_key is not None and self.client is not None

    @property
    def name(self) -> str:
        return "OpenAI Whisper API"

    @property
    def requires_internet(self) -> bool:
        return True


class FFmpegWhisperProvider(SpeechProvider):
    """FFmpeg + whisper.cpp provider for ultra-fast local transcription"""

    def __init__(self):
        self._whisper_cli_path = self._find_whisper_cli()
        self._model_path: Optional[str] = None
        self._model_name = "base"  # Default model
        self._available = self._check_availability()

    def _find_whisper_cli(self) -> Optional[str]:
        """Find whisper-cli executable"""
        import shutil

        return shutil.which("whisper-cli")

    def _check_availability(self) -> bool:
        """Check if whisper-cli is available"""
        if not self._whisper_cli_path:
            print("whisper-cli not found. Install with: brew install whisper-cpp")
            return False

        # Check if we have at least one model
        models_dir = Path(__file__).parent / "whisper_models"
        if not models_dir.exists():
            print("No whisper models directory found")
            return False

        # Look for any available model
        model_files = list(models_dir.glob("ggml-*.bin"))
        if not model_files:
            print(
                "No whisper models found. Run: python download_whisper_models.py download base"
            )
            return False

        # Use the first available model
        self._model_path = str(model_files[0])
        self._model_name = model_files[0].stem.replace("ggml-", "")
        print(f"Found whisper.cpp model: {self._model_name} at {self._model_path}")
        return True

    def set_model(self, model_name: str) -> bool:
        """Set the whisper model to use"""
        models_dir = Path(__file__).parent / "whisper_models"
        model_path = models_dir / f"ggml-{model_name}.bin"

        if not model_path.exists():
            print(f"Model {model_name} not found at {model_path}")
            return False

        self._model_path = str(model_path)
        self._model_name = model_name
        print(f"Switched to model: {model_name}")
        return True

    def transcribe(self, audio_path: str) -> Optional[str]:
        """Transcribe audio using whisper.cpp"""
        if not self.is_available():
            print("FFmpeg Whisper provider not available")
            return None

        try:
            print(f"Starting whisper.cpp transcription for file: {audio_path}")

            # Apply FFmpeg preprocessing
            processor = get_processor()
            processed_audio_path = audio_path

            if processor.ffmpeg_available and processor.noise_reduction_enabled:
                print("Applying FFmpeg preprocessing...")
                processed_audio_path = processor.process_audio_advanced(
                    audio_path, use_arnndn=False
                )

            # Verify input file exists
            if not os.path.exists(processed_audio_path):
                print(f"Error: Audio file does not exist: {processed_audio_path}")
                return None

            # Build whisper-cli command with optimized settings
            cmd = [
                self._whisper_cli_path,
                "-m",
                self._model_path,
                "-f",
                processed_audio_path,
                "--language",
                "ja",
                "--threads",
                "4",  # Use multiple threads
                "--no-prints",  # Reduce output noise
                "--no-timestamps",  # Disable timestamps for cleaner text output
                "--temperature",
                "0.0",  # Deterministic output
                "--beam-size",
                "5",  # Better accuracy
                "--best-of",
                "5",  # Multiple candidates
            ]

            # Enable GPU acceleration if available (Metal on macOS)
            if "--no-gpu" not in cmd:
                # Let whisper.cpp auto-detect and use GPU if available
                pass

            print(f"Running whisper.cpp command: {' '.join(cmd)}")

            # Run whisper-cli
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                timeout=300,  # 5 minute timeout
            )

            if result.returncode != 0:
                print(f"whisper-cli failed with return code {result.returncode}")
                print(f"stderr: {result.stderr}")
                return None

            # Extract text from stdout (no-timestamps mode outputs directly)
            raw_output = result.stdout.strip()

            if raw_output:
                # Clean up the output text
                text = self._clean_transcription_output(raw_output)

                # Clean up processed audio if it's different from original
                if processed_audio_path != audio_path and os.path.exists(
                    processed_audio_path
                ):
                    os.unlink(processed_audio_path)

                if text:
                    print(f"whisper.cpp transcription successful: '{text}'")
                    return text
                else:
                    print("whisper.cpp returned empty text after cleaning")
                    return None
            else:
                print("whisper.cpp returned no output")
                return None

        except subprocess.TimeoutExpired:
            print("whisper.cpp transcription timed out")
            return None
        except Exception as e:
            print(f"whisper.cpp transcription error: {e}")
            import traceback

            traceback.print_exc()
            return None

    def _clean_transcription_output(self, raw_output: str) -> str:
        """Clean whisper.cpp output text"""
        import re

        # Remove timestamp markers like [00:00:00.000 --> 00:00:02.000]
        text = re.sub(r"\[[\d:.\s\->]+\]", "", raw_output)

        # Remove common whisper artifacts
        text = re.sub(r"\(音楽\)", "", text)  # Remove "(音楽)" markers
        text = re.sub(r"\(笑\)", "", text)  # Remove "(笑)" markers
        text = re.sub(r"\(拍手\)", "", text)  # Remove "(拍手)" markers
        text = re.sub(r"\([^)]*\)", "", text)  # Remove other parenthetical markers

        # Clean up whitespace
        text = " ".join(text.split())  # Normalize whitespace
        text = text.strip()

        return text

    def is_available(self) -> bool:
        """Check if whisper.cpp provider is available"""
        return self._available

    @property
    def name(self) -> str:
        return f"FFmpeg + Whisper.cpp — {self._model_name}"

    @property
    def requires_internet(self) -> bool:
        return False

    def get_available_models(self) -> list[str]:
        """Get list of available local models"""
        models_dir = Path(__file__).parent / "whisper_models"
        if not models_dir.exists():
            return []

        model_files = models_dir.glob("ggml-*.bin")
        return [f.stem.replace("ggml-", "") for f in model_files]

    def download_model(self, model_name: str) -> bool:
        """Download a model using the download script"""
        try:
            script_path = Path(__file__).parent / "download_whisper_models.py"
            cmd = [sys.executable, str(script_path), "download", model_name]

            subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"Model {model_name} downloaded successfully")

            # Update availability after download
            self._available = self._check_availability()
            return True

        except subprocess.CalledProcessError as e:
            print(f"Failed to download model {model_name}: {e}")
            return False


class SpeechProviderFactory:
    """Factory for creating speech recognition providers"""

    @staticmethod
    def get_provider(provider_name: Optional[str] = None) -> Optional[SpeechProvider]:
        """
        Get speech provider by name or auto-detect best available

        Args:
            provider_name: Name of provider ('openai', 'ffmpeg', or None for auto)

        Returns:
            SpeechProvider instance or None if no provider available
        """
        load_dotenv(".env.local")

        # If specific provider requested, try to get it
        if provider_name:
            if provider_name.lower() == "openai":
                openai_provider = OpenAIProvider()
                if openai_provider.is_available():
                    return openai_provider
            elif provider_name.lower() in ["ffmpeg", "whisper-cpp"]:
                ffmpeg_provider = FFmpegWhisperProvider()
                if ffmpeg_provider.is_available():
                    return ffmpeg_provider
            print(f"Requested provider '{provider_name}' not available")
            return None

        # Auto-detect best available provider
        provider_name_env = os.getenv("SPEECH_PROVIDER", "auto").lower()

        if provider_name_env == "openai":
            openai_provider = OpenAIProvider()
            if openai_provider.is_available():
                print(f"Using configured provider: {openai_provider.name}")
                return openai_provider
        elif provider_name_env in ["ffmpeg", "whisper-cpp"]:
            ffmpeg_provider = FFmpegWhisperProvider()
            if ffmpeg_provider.is_available():
                print(f"Using configured provider: {ffmpeg_provider.name}")
                return ffmpeg_provider

        # Fallback: try providers in order of preference
        # FFmpeg+Whisper.cpp first (fastest), then OpenAI (most reliable)
        providers = [FFmpegWhisperProvider(), OpenAIProvider()]

        for provider in providers:
            if provider.is_available():
                print(f"Auto-selected provider: {provider.name}")
                return provider

        print("No speech recognition providers available")
        return None

    @staticmethod
    def get_available_providers() -> list[SpeechProvider]:
        """Get list of all available providers"""
        providers = [FFmpegWhisperProvider(), OpenAIProvider()]
        return [p for p in providers if p.is_available()]
