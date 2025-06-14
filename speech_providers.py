#!/usr/bin/env python3
"""
Speech Recognition Providers for Termina
Abstracts different speech recognition backends (OpenAI API, whisper.cpp, etc.)
"""

import os
from abc import ABC, abstractmethod
from typing import Optional
from openai import OpenAI
from dotenv import load_dotenv


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
        load_dotenv('.env.local')
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None
        
    def transcribe(self, audio_path: str) -> Optional[str]:
        """Transcribe audio using OpenAI Whisper API"""
        if not self.is_available():
            print("OpenAI provider not available")
            return None
            
        try:
            print(f"Starting OpenAI transcription for file: {audio_path}")
            
            # Check if file exists and get its size
            if not os.path.exists(audio_path):
                print(f"Error: Audio file does not exist: {audio_path}")
                return None
            
            file_size = os.path.getsize(audio_path)
            print(f"Audio file size: {file_size} bytes")
            
            if file_size == 0:
                print("Error: Audio file is empty")
                return None
            
            with open(audio_path, 'rb') as audio_file:
                print("Sending request to OpenAI Whisper API...")
                transcription = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="ja"  # Japanese language setting
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
            import whisper
            
            print("openai-whisper library available")
            return True
                
        except ImportError:
            print("openai-whisper not installed")
            return False
        except Exception as e:
            print(f"Error checking openai-whisper availability: {e}")
            return False
    
    def _load_model(self, model_name: str = None) -> bool:
        """Load whisper model"""
        try:
            import whisper
            
            # Determine which model to use
            if model_name:
                target_model = model_name
            else:
                target_model = "base"  # Default to base model for good balance
            
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
            
            # Check if file exists
            if not os.path.exists(audio_path):
                print(f"Error: Audio file does not exist: {audio_path}")
                return None
            
            # Load model if needed
            if not self._load_model():
                print("Failed to load openai-whisper model")
                return None
            
            # Load audio manually to avoid ffmpeg dependency issues
            import numpy as np
            import scipy.io.wavfile as wavfile
            
            print(f"Loading audio file manually: {audio_path}")
            try:
                sample_rate, audio_data = wavfile.read(audio_path)
                print(f"Audio loaded: sample_rate={sample_rate}, shape={audio_data.shape}")
                
                # Convert to float32 and normalize
                if audio_data.dtype == np.int16:
                    audio_data = audio_data.astype(np.float32) / 32768.0
                elif audio_data.dtype == np.int32:
                    audio_data = audio_data.astype(np.float32) / 2147483648.0
                
                # Ensure mono
                if len(audio_data.shape) > 1:
                    audio_data = np.mean(audio_data, axis=1)
                
                print(f"Transcribing with model: {self._model_name}")
                result = self._model.transcribe(audio_data, language='ja')
                
            except Exception as audio_error:
                print(f"Manual audio loading failed: {audio_error}")
                print("Falling back to whisper's built-in audio loading...")
                result = self._model.transcribe(audio_path, language='ja')
            
            # Extract text from result
            if isinstance(result, dict) and 'text' in result:
                text = result['text'].strip()
            elif hasattr(result, 'text'):
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
    def get_provider(provider_name: str = None) -> Optional[SpeechProvider]:
        """
        Get speech provider by name or auto-detect best available
        
        Args:
            provider_name: Name of provider ('openai', 'whisper_cpp', or None for auto)
            
        Returns:
            SpeechProvider instance or None if no provider available
        """
        load_dotenv('.env.local')
        
        # If specific provider requested, try to get it
        if provider_name:
            if provider_name.lower() == 'openai':
                provider = OpenAIProvider()
                if provider.is_available():
                    return provider
            elif provider_name.lower() == 'whisper_cpp':
                provider = WhisperCppProvider()
                if provider.is_available():
                    return provider
            print(f"Requested provider '{provider_name}' not available")
            return None
        
        # Auto-detect best available provider
        provider_name_env = os.getenv('SPEECH_PROVIDER', 'auto').lower()
        
        if provider_name_env == 'openai':
            provider = OpenAIProvider()
            if provider.is_available():
                print(f"Using configured provider: {provider.name}")
                return provider
        elif provider_name_env == 'whisper_cpp':
            provider = WhisperCppProvider()
            if provider.is_available():
                print(f"Using configured provider: {provider.name}")
                return provider
        
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