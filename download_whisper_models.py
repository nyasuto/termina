#!/usr/bin/env python3
"""
Whisper.cpp model downloader for Termina
Downloads GGML models for local inference
"""

import subprocess
import sys
from pathlib import Path

# Model configurations with sizes and checksums
MODELS = {
    "tiny": {
        "url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.bin",
        "size_mb": 39,
        "description": "Fastest, lowest accuracy",
    },
    "base": {
        "url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin",
        "size_mb": 142,
        "description": "Good balance of speed and accuracy",
    },
    "small": {
        "url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin",
        "size_mb": 466,
        "description": "Better accuracy, slower",
    },
    "medium": {
        "url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium.bin",
        "size_mb": 1500,
        "description": "High accuracy, requires more memory",
    },
    "large-v3": {
        "url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3.bin",
        "size_mb": 2900,
        "description": "Highest accuracy, slowest (GPU recommended)",
    },
}

MODELS_DIR = Path(__file__).parent / "whisper_models"


def create_models_directory():
    """Create models directory if it doesn't exist"""
    MODELS_DIR.mkdir(exist_ok=True)
    print(f"📁 Models directory: {MODELS_DIR}")


def download_model(model_name: str, force: bool = False) -> bool:
    """
    Download a specific model

    Args:
        model_name: Name of the model to download
        force: Force re-download even if file exists

    Returns:
        True if successful, False otherwise
    """
    if model_name not in MODELS:
        print(f"❌ Unknown model: {model_name}")
        print(f"Available models: {', '.join(MODELS.keys())}")
        return False

    model_info = MODELS[model_name]
    model_path = MODELS_DIR / f"ggml-{model_name}.bin"

    # Check if model already exists
    if model_path.exists() and not force:
        print(f"✅ Model {model_name} already exists at {model_path}")
        return True

    print(f"📥 Downloading {model_name} model...")
    print(f"   Size: ~{model_info['size_mb']}MB")
    print(f"   Description: {model_info['description']}")
    print(f"   URL: {model_info['url']}")

    try:
        # Use curl for better progress display and resume capability
        cmd = [
            "curl",
            "-L",
            "-o",
            str(model_path),
            "--progress-bar",
            "-C",
            "-",  # Resume partial downloads
            model_info["url"],
        ]

        subprocess.run(cmd, check=True)

        if model_path.exists():
            file_size_mb = model_path.stat().st_size / (1024 * 1024)
            print(f"✅ Successfully downloaded {model_name} ({file_size_mb:.1f}MB)")
            return True
        else:
            print("❌ Download failed - file not found")
            return False

    except subprocess.CalledProcessError as e:
        print(f"❌ Download failed: {e}")
        # Clean up partial download
        if model_path.exists():
            model_path.unlink()
        return False
    except KeyboardInterrupt:
        print("\n⏹️  Download interrupted")
        # Clean up partial download
        if model_path.exists():
            model_path.unlink()
        return False


def list_models():
    """List available models with their info"""
    print("🎯 Available Whisper Models:")
    print()
    for model_name, info in MODELS.items():
        model_path = MODELS_DIR / f"ggml-{model_name}.bin"
        status = "✅ Downloaded" if model_path.exists() else "⬜ Not downloaded"

        print(f"  {model_name:10} | {info['size_mb']:4}MB | {status}")
        print(f"             | {info['description']}")
        print()


def check_whisper_cpp():
    """Check if whisper-cli is available"""
    try:
        result = subprocess.run(
            ["whisper-cli", "--help"], capture_output=True, text=True, check=False
        )
        if result.returncode == 0:
            print("✅ whisper-cli is available")
            return True
        else:
            print("❌ whisper-cli not found")
            return False
    except FileNotFoundError:
        print("❌ whisper-cli not installed")
        print("   Install with: brew install whisper-cpp")
        return False


def main():
    """Main CLI interface"""
    if len(sys.argv) < 2:
        print("🎤 Termina Whisper Model Downloader")
        print()
        print("Usage:")
        print("  python download_whisper_models.py list")
        print("  python download_whisper_models.py download <model_name>")
        print("  python download_whisper_models.py download-all")
        print("  python download_whisper_models.py check")
        print()
        list_models()
        return

    command = sys.argv[1].lower()

    # Create models directory
    create_models_directory()

    if command == "list":
        list_models()

    elif command == "check":
        check_whisper_cpp()
        list_models()

    elif command == "download":
        if len(sys.argv) < 3:
            print("❌ Please specify model name")
            print(f"Available: {', '.join(MODELS.keys())}")
            return

        model_name = sys.argv[2]
        force = "--force" in sys.argv

        if download_model(model_name, force):
            print(f"✅ Model {model_name} ready to use!")
            print(f"   Path: {MODELS_DIR / f'ggml-{model_name}.bin'}")
        else:
            print(f"❌ Failed to download {model_name}")
            sys.exit(1)

    elif command == "download-all":
        print("📥 Downloading all models...")
        force = "--force" in sys.argv
        success_count = 0

        for model_name in MODELS:
            if download_model(model_name, force):
                success_count += 1
            print()  # Add spacing between downloads

        print(f"✅ Successfully downloaded {success_count}/{len(MODELS)} models")

    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: list, download, download-all, check")
        sys.exit(1)


if __name__ == "__main__":
    main()
