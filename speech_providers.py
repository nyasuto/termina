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
    """Local whisper.cpp provider (placeholder for future implementation)"""
    
    def __init__(self):
        # TODO: Initialize whisper.cpp bindings
        self._available = False
        
    def transcribe(self, audio_path: str) -> Optional[str]:
        """Transcribe audio using local whisper.cpp"""
        if not self.is_available():
            print("whisper.cpp provider not available")
            return None
            
        try:
            print(f"Starting whisper.cpp transcription for file: {audio_path}")
            # TODO: Implement whisper.cpp transcription
            print("whisper.cpp transcription not yet implemented")
            return None
                
        except Exception as e:
            print(f"whisper.cpp transcription error: {e}")
            return None
    
    def is_available(self) -> bool:
        """Check if whisper.cpp is available"""
        # TODO: Check if whisper.cpp bindings are installed and models are available
        return self._available
    
    @property
    def name(self) -> str:
        return "Local Whisper (whisper.cpp)"
    
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