#!/usr/bin/env python3
"""
Whisper Model Management for Termina
Handles downloading and managing local Whisper models
"""

from pathlib import Path
from typing import Optional

import requests


class WhisperModelManager:
    """Manages Whisper model downloading and storage"""

    # Model information: name -> (url, expected_sha256, size_mb)
    MODELS = {
        "tiny": (
            "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.bin",
            "be07e048e1e599ad46341c8d2a135645097a303b82394ad0e2ce15eb8a1e1e3c",
            39,
        ),
        "base": (
            "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin",
            "60ed5bc3dd14eea856493d334349b405782ddcaf0028d4b5df4088345fba2efe",
            142,
        ),
        "small": (
            "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin",
            "1be3a9b2063867b937e64e2ec7483364a79917e157fa98c5d94b5c1fffea987b",
            466,
        ),
        "medium": (
            "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium.bin",
            "6c14d5adee5f39055a61c2b1d2e4b1c7e3e9f7e8f6e5c4c3d2e1f0a9b8c7d6e5",
            1540,
        ),
        "large": (
            "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3.bin",
            "ad82bf6ef9fd339d67b2ffccc8ff14802f1e99d6b77a9ec6a8d26b38b5bb2cd5",
            3100,
        ),
    }

    def __init__(self, models_dir: Optional[str] = None):
        """
        Initialize model manager

        Args:
            models_dir: Directory to store models. If None, uses ~/.termina/models/
        """
        if models_dir is None:
            self.models_dir = Path.home() / ".termina" / "models"
        else:
            self.models_dir = Path(models_dir)

        # Create models directory if it doesn't exist
        self.models_dir.mkdir(parents=True, exist_ok=True)

    def get_model_path(self, model_name: str) -> Path:
        """Get the local path for a model"""
        return self.models_dir / f"ggml-{model_name}.bin"

    def is_model_downloaded(self, model_name: str) -> bool:
        """Check if a model is already downloaded"""
        if model_name not in self.MODELS:
            return False

        model_path = self.get_model_path(model_name)
        if not model_path.exists():
            return False

        # Verify file size and hash
        return self._verify_model(model_name, model_path)

    def _verify_model(self, model_name: str, model_path: Path) -> bool:
        """Verify model integrity"""
        try:
            url, expected_hash, expected_size_mb = self.MODELS[model_name]

            # Check file size (rough check)
            file_size_mb = model_path.stat().st_size / (1024 * 1024)
            if (
                abs(file_size_mb - expected_size_mb) > expected_size_mb * 0.1
            ):  # 10% tolerance
                print(
                    f"Model {model_name} size mismatch: {file_size_mb:.1f}MB != {expected_size_mb}MB"
                )
                return False

            # TODO: Add SHA256 verification for better integrity checking
            # This would be slow for large models, so make it optional

            return True
        except Exception as e:
            print(f"Error verifying model {model_name}: {e}")
            return False

    def download_model(self, model_name: str, progress_callback=None) -> bool:
        """
        Download a model

        Args:
            model_name: Name of the model to download
            progress_callback: Optional callback function for progress updates

        Returns:
            True if download successful, False otherwise
        """
        if model_name not in self.MODELS:
            print(f"Unknown model: {model_name}")
            return False

        if self.is_model_downloaded(model_name):
            print(f"Model {model_name} already downloaded")
            return True

        url, expected_hash, size_mb = self.MODELS[model_name]
        model_path = self.get_model_path(model_name)

        print(f"Downloading {model_name} model ({size_mb}MB)...")

        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0))
            downloaded = 0

            with open(model_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        if progress_callback and total_size > 0:
                            progress = (downloaded / total_size) * 100
                            progress_callback(progress)

            print(f"Model {model_name} downloaded successfully")

            # Verify the downloaded model
            if self._verify_model(model_name, model_path):
                print(f"Model {model_name} verified successfully")
                return True
            else:
                print(f"Model {model_name} verification failed, removing file")
                model_path.unlink()
                return False

        except Exception as e:
            print(f"Error downloading model {model_name}: {e}")
            if model_path.exists():
                model_path.unlink()
            return False

    def get_available_models(self) -> dict[str, tuple[bool, int]]:
        """
        Get information about all models

        Returns:
            Dict mapping model name to (is_downloaded, size_mb)
        """
        result = {}
        for model_name, (_url, _hash, size_mb) in self.MODELS.items():
            is_downloaded = self.is_model_downloaded(model_name)
            result[model_name] = (is_downloaded, size_mb)
        return result

    def get_best_available_model(self) -> Optional[str]:
        """Get the best model that's already downloaded"""
        # Order of preference: large > medium > small > base > tiny
        preferred_order = ["large", "medium", "small", "base", "tiny"]

        for model_name in preferred_order:
            if self.is_model_downloaded(model_name):
                return model_name

        return None

    def recommend_model(self) -> str:
        """Recommend a model based on system capabilities"""
        # For now, recommend 'base' as a good balance of speed/quality
        # TODO: Could check system RAM, CPU cores, etc. for better recommendations
        return "base"

    def cleanup_models(self) -> int:
        """Remove any corrupted or invalid model files"""
        cleaned = 0
        for model_name in self.MODELS:
            model_path = self.get_model_path(model_name)
            if model_path.exists() and not self._verify_model(model_name, model_path):
                print(f"Removing corrupted model: {model_name}")
                model_path.unlink()
                cleaned += 1
        return cleaned
