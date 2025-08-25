#!/usr/bin/env python3
"""
Speech Recognition Providers for Termina
Abstracts different speech recognition backends (OpenAI API, whisper.cpp, etc.)
"""

import os
from abc import ABC, abstractmethod
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


class WhisperCppProvider(SpeechProvider):
    """Local openai-whisper provider"""

    def __init__(self):
        self._model = None
        self._model_name = None
        self._available = self._check_availability()

    def _check_availability(self) -> bool:
        """Check if local whisper is available"""
        try:
            # Check if openai-whisper is installed
            import importlib.util

            if importlib.util.find_spec("whisper") is None:
                raise ImportError("openai-whisper not installed")

            print("openai-whisper library available")
            return True

        except ImportError:
            print("openai-whisper not installed")
            return False
        except Exception as e:
            print(f"Error checking openai-whisper availability: {e}")
            return False

    def _load_model(self, model_name: Optional[str] = None) -> bool:
        """Load whisper model"""
        try:
            import whisper  # noqa: F401

            # Determine which model to use (prioritize accuracy over speed)
            # Use large model for best accuracy (if user has sufficient resources)
            target_model = (
                model_name or "large"
            )  # Best accuracy, requires more memory/CPU

            # Load the model if not already loaded
            if self._model_name != target_model:
                print(f"Loading openai-whisper model: {target_model}")
                self._model = whisper.load_model(target_model)
                self._model_name = target_model
                print(f"Model {target_model} loaded successfully")

            return True

        except Exception as e:
            print(f"Error loading openai-whisper model: {e}")
            import traceback

            traceback.print_exc()
            return False

    def transcribe(self, audio_path: str) -> Optional[str]:
        """Transcribe audio using local openai-whisper"""
        if not self.is_available():
            print("openai-whisper provider not available")
            return None

        try:
            print(f"Starting openai-whisper transcription for file: {audio_path}")

            # Apply FFmpeg noise reduction if available
            processor = get_processor()
            if processor.ffmpeg_available and processor.noise_reduction_enabled:
                print("Applying FFmpeg noise reduction before transcription...")
                audio_path = processor.process_audio(audio_path)

            # Check if file exists
            if not os.path.exists(audio_path):
                print(f"Error: Audio file does not exist: {audio_path}")
                return None

            # Load model if needed
            if not self._load_model():
                print("Failed to load openai-whisper model")
                return None

            # Load audio manually with proper preprocessing for Whisper
            import numpy as np
            import scipy.io.wavfile as wavfile
            from scipy import signal

            print(f"Loading audio file manually: {audio_path}")
            try:
                sample_rate, audio_data = wavfile.read(audio_path)
                print(
                    f"Audio loaded: sample_rate={sample_rate}, shape={audio_data.shape}, dtype={audio_data.dtype}"
                )

                # Convert to float32 and normalize properly
                if audio_data.dtype == np.int16:
                    audio_data = audio_data.astype(np.float32) / 32768.0
                elif audio_data.dtype == np.int32:
                    audio_data = audio_data.astype(np.float32) / 2147483648.0
                elif audio_data.dtype == np.uint8:
                    audio_data = (audio_data.astype(np.float32) - 128.0) / 128.0

                # Ensure mono
                if len(audio_data.shape) > 1:
                    audio_data = np.mean(audio_data, axis=1)

                # Resample to 16kHz if needed (Whisper expects 16kHz)
                if sample_rate != 16000:
                    print(f"Resampling from {sample_rate}Hz to 16kHz")
                    num_samples = int(len(audio_data) * 16000 / sample_rate)
                    audio_data = signal.resample(audio_data, num_samples)
                    sample_rate = 16000

                # Improve audio quality with noise reduction and normalization
                # Apply simple noise gate to reduce background noise
                noise_threshold = np.std(audio_data) * 0.1
                audio_data = np.where(
                    np.abs(audio_data) < noise_threshold, 0, audio_data
                )

                # Normalize audio to optimal range for Whisper
                if np.max(np.abs(audio_data)) > 0:
                    audio_data = audio_data / (
                        np.max(np.abs(audio_data)) * 1.1
                    )  # Leave some headroom

                # Ensure audio length is reasonable (not too short/long)
                if len(audio_data) < 1600:  # Less than 0.1 seconds
                    print("Audio too short, padding with silence")
                    audio_data = np.pad(
                        audio_data,
                        (0, 1600 - len(audio_data)),
                        "constant",
                        constant_values=0,
                    )

                # Apply gentle high-pass filter to remove low-frequency noise
                if sample_rate == 16000:
                    from scipy.signal import butter, filtfilt

                    nyquist = sample_rate / 2
                    low_cutoff = 80 / nyquist  # Remove frequencies below 80Hz
                    b, a = butter(1, low_cutoff, btype="high")
                    audio_data = filtfilt(b, a, audio_data)

                print(
                    f"Preprocessed audio: length={len(audio_data)}, sample_rate={sample_rate}"
                )
                print(
                    f"Audio stats: min={np.min(audio_data):.4f}, max={np.max(audio_data):.4f}, mean={np.mean(audio_data):.4f}"
                )

                # Ensure audio array has positive strides and correct dtype for PyTorch compatibility
                audio_data = np.ascontiguousarray(audio_data.copy()).astype(np.float32)
                print(
                    f"Audio array made contiguous for PyTorch compatibility: dtype={audio_data.dtype}"
                )

                print(f"Transcribing with model: {self._model_name}")
                # Optimize transcription settings for best accuracy
                result = self._model.transcribe(
                    audio_data,
                    language="ja",
                    verbose=True,
                    beam_size=5,  # Use beam search for better accuracy (default is 5)
                    best_of=5,  # Generate multiple candidates and pick best
                    temperature=0.0,  # Use deterministic decoding for consistency
                    patience=1.0,  # Wait longer for better results
                    length_penalty=1.0,  # Don't penalize longer sequences
                    suppress_tokens=[-1],  # Suppress silence token
                    initial_prompt="以下は日本語の音声です。",  # Japanese prompt for better context
                    condition_on_previous_text=False,  # Don't condition on previous text for short clips
                    fp16=False,  # Use FP32 for better precision on CPU
                )

            except Exception as audio_error:
                print(f"Manual audio loading failed: {audio_error}")
                import traceback

                traceback.print_exc()
                print("Falling back to whisper's built-in audio loading...")
                result = self._model.transcribe(audio_path, language="ja")

            # Extract text from result
            if isinstance(result, dict) and "text" in result:
                text = result["text"].strip()
            elif hasattr(result, "text"):
                text = result.text.strip()
            elif isinstance(result, str):
                text = result.strip()
            else:
                print(f"Unexpected result format: {type(result)}")
                return None

            print(f"openai-whisper transcription successful: '{text}'")
            return text if text else None

        except Exception as e:
            print(f"openai-whisper transcription error: {e}")
            import traceback

            traceback.print_exc()
            return None

    def is_available(self) -> bool:
        """Check if whisper.cpp is available"""
        return self._available

    @property
    def name(self) -> str:
        return f"Local Whisper ({self._model_name or 'openai-whisper'})"

    @property
    def requires_internet(self) -> bool:
        return False


class SpeechProviderFactory:
    """Factory for creating speech recognition providers"""

    @staticmethod
    def get_provider(provider_name: Optional[str] = None) -> Optional[SpeechProvider]:
        """
        Get speech provider by name or auto-detect best available

        Args:
            provider_name: Name of provider ('openai', 'whisper_cpp', or None for auto)

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
            elif provider_name.lower() == "whisper_cpp":
                whisper_provider = WhisperCppProvider()
                if whisper_provider.is_available():
                    return whisper_provider
            print(f"Requested provider '{provider_name}' not available")
            return None

        # Auto-detect best available provider
        provider_name_env = os.getenv("SPEECH_PROVIDER", "auto").lower()

        if provider_name_env == "openai":
            openai_provider = OpenAIProvider()
            if openai_provider.is_available():
                print(f"Using configured provider: {openai_provider.name}")
                return openai_provider
        elif provider_name_env == "whisper_cpp":
            whisper_provider = WhisperCppProvider()
            if whisper_provider.is_available():
                print(f"Using configured provider: {whisper_provider.name}")
                return whisper_provider

        # Fallback: try providers in order of preference
        providers = [OpenAIProvider(), WhisperCppProvider()]

        for provider in providers:
            if provider.is_available():
                print(f"Auto-selected provider: {provider.name}")
                return provider

        print("No speech recognition providers available")
        return None

    @staticmethod
    def get_available_providers() -> list[SpeechProvider]:
        """Get list of all available providers"""
        providers = [OpenAIProvider(), WhisperCppProvider()]
        return [p for p in providers if p.is_available()]
