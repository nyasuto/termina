#!/usr/bin/env python3
"""
FFmpeg Audio Processor for Termina
Provides AI-based noise reduction and audio enhancement using FFmpeg filters
"""

import os
import subprocess
import tempfile
import shutil
from typing import Optional, Dict, Any
from pathlib import Path


class FFmpegAudioProcessor:
    """Process audio using FFmpeg for noise reduction and quality enhancement"""

    def __init__(self):
        self.ffmpeg_available = self._check_ffmpeg()
        self.noise_reduction_enabled = True
        self.filters = self._get_default_filters()

    def _check_ffmpeg(self) -> bool:
        """Check if FFmpeg is available on the system"""
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"], capture_output=True, text=True, check=False
            )
            return result.returncode == 0
        except FileNotFoundError:
            print("FFmpeg not found. Audio enhancement will be disabled.")
            return False

    def _get_default_filters(self) -> Dict[str, Any]:
        """Get default audio filter configuration"""
        return {
            "highpass": {
                "enabled": True,
                "frequency": 80,
                "description": "Remove low-frequency noise",
            },
            "lowpass": {
                "enabled": True,
                "frequency": 8000,
                "description": "Remove high-frequency noise",
            },
            "volume_normalization": {
                "enabled": True,
                "level": 1.5,
                "description": "Normalize audio volume",
            },
            "noise_gate": {
                "enabled": True,
                "threshold": -50,
                "description": "Remove background noise below threshold",
            },
        }

    def process_audio(self, input_path: str, output_path: Optional[str] = None) -> str:
        """
        Process audio file with noise reduction and enhancement

        Args:
            input_path: Path to input audio file
            output_path: Optional path for output file. If None, overwrites input.

        Returns:
            Path to processed audio file
        """
        if not self.ffmpeg_available:
            print("FFmpeg not available, returning original audio")
            return input_path

        if not self.noise_reduction_enabled:
            print("Noise reduction disabled, returning original audio")
            return input_path

        # Create temporary output file if no output path specified
        if output_path is None:
            temp_fd, temp_path = tempfile.mkstemp(suffix=".wav")
            os.close(temp_fd)
            output_path = temp_path
            overwrite_input = True
        else:
            overwrite_input = False

        try:
            # Build filter chain
            filter_chain = self._build_filter_chain()

            # Build FFmpeg command
            cmd = [
                "ffmpeg",
                "-i",
                input_path,
                "-af",
                filter_chain,
                "-ar",
                "16000",  # Whisper optimal sample rate
                "-ac",
                "1",  # Mono audio
                "-c:a",
                "pcm_s16le",  # 16-bit PCM
                "-y",  # Overwrite output
                output_path,
            ]

            print(f"Processing audio with FFmpeg filters: {filter_chain}")

            # Run FFmpeg
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)

            if result.returncode != 0:
                print(f"FFmpeg processing failed: {result.stderr}")
                # Return original file if processing fails
                if overwrite_input:
                    os.unlink(output_path)
                return input_path

            # If we need to overwrite the input file
            if overwrite_input:
                shutil.move(output_path, input_path)
                return input_path

            return output_path

        except Exception as e:
            print(f"Error processing audio with FFmpeg: {e}")
            # Clean up temporary file if created
            if overwrite_input and os.path.exists(output_path):
                os.unlink(output_path)
            return input_path

    def _build_filter_chain(self) -> str:
        """Build FFmpeg audio filter chain based on enabled filters"""
        filters = []

        # High-pass filter to remove low-frequency noise
        if self.filters["highpass"]["enabled"]:
            filters.append(f"highpass=f={self.filters['highpass']['frequency']}")

        # Low-pass filter to remove high-frequency noise
        if self.filters["lowpass"]["enabled"]:
            filters.append(f"lowpass=f={self.filters['lowpass']['frequency']}")

        # Volume normalization
        if self.filters["volume_normalization"]["enabled"]:
            filters.append(f"volume={self.filters['volume_normalization']['level']}")

        # Simple noise gate using silenceremove
        if self.filters["noise_gate"]["enabled"]:
            threshold = self.filters["noise_gate"]["threshold"]
            filters.append(
                f"silenceremove=start_periods=0:start_duration=0.1:start_threshold={threshold}dB:detection=peak"
            )

        # Join filters with comma
        return ",".join(filters) if filters else "anull"

    def set_noise_reduction(self, enabled: bool) -> None:
        """Enable or disable noise reduction"""
        self.noise_reduction_enabled = enabled
        print(f"Noise reduction {'enabled' if enabled else 'disabled'}")

    def configure_filter(self, filter_name: str, **kwargs) -> None:
        """
        Configure individual filter parameters

        Args:
            filter_name: Name of the filter to configure
            **kwargs: Filter-specific parameters
        """
        if filter_name in self.filters:
            self.filters[filter_name].update(kwargs)
            print(f"Updated {filter_name} filter: {self.filters[filter_name]}")
        else:
            print(f"Unknown filter: {filter_name}")

    def get_filter_status(self) -> Dict[str, Any]:
        """Get current filter configuration status"""
        return {
            "ffmpeg_available": self.ffmpeg_available,
            "noise_reduction_enabled": self.noise_reduction_enabled,
            "filters": self.filters,
        }

    def process_audio_advanced(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        use_arnndn: bool = False,
    ) -> str:
        """
        Process audio with advanced filters including AI-based noise reduction

        Args:
            input_path: Path to input audio file
            output_path: Optional path for output file
            use_arnndn: Use AI-based RNN noise reduction (requires FFmpeg with arnndn)

        Returns:
            Path to processed audio file
        """
        if not self.ffmpeg_available:
            return input_path

        if not self.noise_reduction_enabled:
            return input_path

        # Create temporary output file if no output path specified
        if output_path is None:
            temp_fd, temp_path = tempfile.mkstemp(suffix=".wav")
            os.close(temp_fd)
            output_path = temp_path
            overwrite_input = True
        else:
            overwrite_input = False

        try:
            # Build advanced filter chain
            filters = []

            # Basic filters
            filters.append("highpass=f=80")  # Remove rumble
            filters.append("lowpass=f=8000")  # Remove high-freq noise

            # AI-based noise reduction if available and requested
            if use_arnndn:
                # Check if arnndn is available
                check_cmd = ["ffmpeg", "-filters"]
                result = subprocess.run(check_cmd, capture_output=True, text=True)
                if "arnndn" in result.stdout:
                    filters.append("arnndn")
                    print("Using AI-based noise reduction (arnndn)")
                else:
                    print("arnndn filter not available, using standard filters")

            # Dynamic range compression for speech
            filters.append("compand=attacks=0.1:decays=0.3:gain=2")

            # Normalize volume
            filters.append("loudnorm=I=-16:TP=-1.5:LRA=11")

            filter_chain = ",".join(filters)

            # Build FFmpeg command
            cmd = [
                "ffmpeg",
                "-i",
                input_path,
                "-af",
                filter_chain,
                "-ar",
                "16000",
                "-ac",
                "1",
                "-c:a",
                "pcm_s16le",
                "-y",
                output_path,
            ]

            print(f"Processing with advanced filters: {filter_chain}")

            # Run FFmpeg
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)

            if result.returncode != 0:
                print(f"Advanced processing failed: {result.stderr}")
                if overwrite_input:
                    os.unlink(output_path)
                return input_path

            # If we need to overwrite the input file
            if overwrite_input:
                shutil.move(output_path, input_path)
                return input_path

            return output_path

        except Exception as e:
            print(f"Error in advanced audio processing: {e}")
            if overwrite_input and os.path.exists(output_path):
                os.unlink(output_path)
            return input_path


# Singleton instance
_processor_instance = None


def get_processor() -> FFmpegAudioProcessor:
    """Get singleton instance of FFmpegAudioProcessor"""
    global _processor_instance
    if _processor_instance is None:
        _processor_instance = FFmpegAudioProcessor()
    return _processor_instance
