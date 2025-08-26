#!/usr/bin/env python3
"""
Termina - macOS Menu Bar Voice Input Application
Records audio, transcribes with OpenAI Whisper, and pastes text to active applications
Supports manual recording controls and global hotkeys (Cmd+Shift+V)
"""

import os
import subprocess
import tempfile
import threading

import rumps
import scipy.io.wavfile as wavfile
import sounddevice as sd
from dotenv import load_dotenv
from pynput import keyboard

from ffmpeg_processor import get_processor
from speech_providers import SpeechProviderFactory


class TerminaApp(rumps.App):
    def __init__(self):
        super().__init__("🎤", quit_button=None)

        # Load environment variables from .env.local
        load_dotenv(".env.local")

        # Initialize speech recognition provider
        self.speech_provider = SpeechProviderFactory.get_provider()
        if not self.speech_provider:
            rumps.alert(
                "Termina Setup Error",
                "No speech recognition provider available. Please check your configuration.",
            )

        # Recording settings (use 16kHz for Whisper compatibility)
        self.sample_rate = 16000
        self.is_recording = False
        self.audio_data = None
        self.recording_thread = None
        self.recording_start_time = None

        # Hotkey settings
        self.hotkey_listener = None
        self.setup_hotkeys()

        # Menu items
        self.start_item = rumps.MenuItem(
            "Start Recording", callback=self.toggle_recording
        )
        self.provider_menu = self._create_provider_menu()
        self.audio_settings_menu = self._create_audio_settings_menu()

        self.menu = [
            self.start_item,
            rumps.separator,
            self.provider_menu,
            self.audio_settings_menu,
            rumps.separator,
            rumps.MenuItem("Hotkey: ⌘+Shift+V", callback=None),
            rumps.separator,
            rumps.MenuItem("Quit", callback=rumps.quit_application),
        ]

    def toggle_recording(self, _):
        """Toggle recording state"""
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        """Start audio recording"""
        import time

        self.is_recording = True
        self.recording_start_time = time.time()
        self.start_item.title = "Stop Recording"
        rumps.notification(
            "Termina",
            "Recording Started",
            "Recording... Click 'Stop Recording' to finish",
        )

        # Start recording in a separate thread
        self.recording_thread = threading.Thread(
            target=self._start_continuous_recording
        )
        self.recording_thread.daemon = True
        self.recording_thread.start()

    def stop_recording(self):
        """Stop audio recording and process"""
        if not self.is_recording:
            return

        self.is_recording = False
        self.start_item.title = "Start Recording"
        rumps.notification("Termina", "Recording Stopped", "Processing audio...")

        # Stop the recording and wait for it to complete
        sd.stop()
        sd.wait()  # Wait for recording to finish

        # Process the recorded audio
        if self.audio_data is not None:
            thread = threading.Thread(target=self._process_audio)
            thread.daemon = True
            thread.start()

    def _start_continuous_recording(self):
        """Start continuous recording until stopped"""
        try:
            # Start recording with a large buffer (10 minutes max)
            max_duration = 600  # 10 minutes
            self.audio_data = sd.rec(
                int(max_duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1,
                dtype="int16",
            )
        except Exception as e:
            rumps.notification("Termina", "Error", f"Recording failed: {str(e)}")
            self.is_recording = False
            self.start_item.title = "Start Recording"

    def _process_audio(self):
        """Process the recorded audio"""
        try:
            import time

            print("Starting audio processing...")

            if self.audio_data is None:
                print("Error: No audio data to process")
                rumps.notification("Termina", "Error", "No audio data to process")
                return

            print(
                f"Audio data shape: {self.audio_data.shape if hasattr(self.audio_data, 'shape') else 'No shape attribute'}"
            )

            # Calculate actual recorded length based on time
            if self.recording_start_time:
                recording_duration = time.time() - self.recording_start_time
                actual_frames = int(recording_duration * self.sample_rate)
                print(f"Recording duration: {recording_duration:.2f} seconds")
                print(f"Calculated frames: {actual_frames}")

                # Trim audio data to actual recording length
                if actual_frames > 0 and actual_frames < len(self.audio_data):
                    audio_data = self.audio_data[:actual_frames]
                    print(f"Trimmed audio data to {actual_frames} frames")
                else:
                    audio_data = self.audio_data
                    print("Using full audio buffer")
            else:
                audio_data = self.audio_data
                print("No start time recorded, using full buffer")

            print(
                f"Final audio data shape: {audio_data.shape if hasattr(audio_data, 'shape') else 'No shape attribute'}"
            )

            # Validate audio data
            if len(audio_data) == 0:
                print("Error: Audio data is empty")
                rumps.notification("Termina", "Error", "Recorded audio is empty")
                return

            # Check for actual audio content (not just silence)
            import numpy as np

            audio_abs = np.abs(audio_data)
            max_amplitude = np.max(audio_abs)
            rms_amplitude = np.sqrt(np.mean(audio_abs**2))
            print(
                f"Audio validation: max_amplitude={max_amplitude}, rms_amplitude={rms_amplitude}"
            )

            if max_amplitude < 100:  # Very low amplitude threshold for int16
                print("Warning: Audio amplitude is very low, might be mostly silence")
                rumps.notification(
                    "Termina", "Warning", "Audio seems very quiet, please speak louder"
                )

            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = temp_file.name
                print(f"Saving audio to temporary file: {temp_path}")
                wavfile.write(temp_path, self.sample_rate, audio_data)
                print("Audio file saved successfully")

            # Transcribe with Whisper
            print("Starting transcription...")
            transcription = self._transcribe_audio(temp_path)

            # Clean up temporary file
            print("Cleaning up temporary file...")
            os.unlink(temp_path)

            if transcription:
                print(f"Transcription result: '{transcription}'")
                # Paste text to current application
                print("Attempting to paste text...")
                self._paste_text(transcription)
                rumps.notification("Termina", "Text Pasted", f"Pasted: {transcription}")
                print("Text pasted successfully")
            else:
                print("No transcription result received")
                rumps.notification("Termina", "Error", "Failed to transcribe audio")

        except Exception as e:
            print(f"Processing failed with error: {str(e)}")
            import traceback

            traceback.print_exc()
            rumps.notification("Termina", "Error", f"Processing failed: {str(e)}")
        finally:
            self.audio_data = None
            self.recording_start_time = None
            print("Audio processing completed")

    def _transcribe_audio(self, audio_path):
        """Transcribe audio using configured speech provider"""
        if not self.speech_provider:
            print("No speech provider available")
            return None

        try:
            print(f"Starting transcription with {self.speech_provider.name}")
            result = self.speech_provider.transcribe(audio_path)

            if result:
                print(f"Transcription successful: '{result}'")
            else:
                print("Transcription failed or returned empty result")

            return result

        except Exception as e:
            print(f"Transcription error: {e}")
            import traceback

            traceback.print_exc()
            return None

    def _paste_text(self, text):
        """Paste text to the currently active application using AppleScript"""
        try:
            print(f"Attempting to paste text: '{text}'")

            # Use clipboard method for safer text pasting
            applescript = f"""
            set the clipboard to "{text}"
            tell application "System Events"
                keystroke "v" using command down
            end tell
            """

            print("Executing AppleScript...")
            result = subprocess.run(
                ["osascript", "-e", applescript],
                capture_output=True,
                text=True,
                check=True,
            )
            print(f"AppleScript executed successfully: {result}")

        except subprocess.CalledProcessError as e:
            print(f"AppleScript error: {e}")
            print(f"Error output: {e.stderr if hasattr(e, 'stderr') else 'No stderr'}")
            rumps.notification("Termina", "Error", "Failed to paste text")
        except Exception as e:
            print(f"Unexpected error in paste_text: {e}")
            import traceback

            traceback.print_exc()
            rumps.notification("Termina", "Error", f"Paste failed: {str(e)}")

    def setup_hotkeys(self):
        """Setup global hotkeys"""
        try:
            print("Setting up global hotkeys...")
            # Define hotkey combination: Cmd+Shift+V
            self.hotkey_listener = keyboard.GlobalHotKeys(
                {"<cmd>+<shift>+v": self.hotkey_toggle_recording}
            )
            self.hotkey_listener.start()
            print("Global hotkeys initialized: Cmd+Shift+V")
        except Exception as e:
            print(f"Failed to setup hotkeys: {e}")
            rumps.notification(
                "Termina",
                "Hotkey Error",
                "Failed to setup global hotkeys. Check accessibility permissions.",
            )

    def hotkey_toggle_recording(self):
        """Handle hotkey press for recording toggle"""
        try:
            print("Hotkey pressed: Cmd+Shift+V")
            self.toggle_recording(None)
        except Exception as e:
            print(f"Hotkey error: {e}")

    def cleanup(self):
        """Cleanup resources on app exit"""
        print("Cleaning up resources...")
        if self.hotkey_listener:
            self.hotkey_listener.stop()
            print("Hotkey listener stopped")

        if self.is_recording:
            print("Stopping recording...")
            self.stop_recording()

    def _create_provider_menu(self):
        """Create speech provider selection menu"""
        from speech_providers import SpeechProviderFactory

        provider_menu = rumps.MenuItem("Speech Provider")

        # Get available providers
        available_providers = SpeechProviderFactory.get_available_providers()

        if not available_providers:
            provider_menu.add(rumps.MenuItem("No providers available", callback=None))
            return provider_menu

        # Add provider options
        current_provider_name = (
            self.speech_provider.name if self.speech_provider else "None"
        )

        for provider in available_providers:
            is_current = provider.name == current_provider_name
            menu_title = f"● {provider.name}" if is_current else f"○ {provider.name}"

            # Add internet requirement indicator
            if provider.requires_internet:
                menu_title += " 🌐"
            else:
                menu_title += " 💻"

            item = rumps.MenuItem(
                menu_title, callback=lambda sender, p=provider: self._switch_provider(p)
            )
            provider_menu.add(item)

        # Add separator and model management for whisper.cpp
        if any(not p.requires_internet for p in available_providers):
            provider_menu.add(rumps.separator)
            provider_menu.add(
                rumps.MenuItem("Manage Local Models...", callback=self._manage_models)
            )

            # Add model size selection for local whisper
            model_menu = rumps.MenuItem("Select Model Size")
            model_sizes = [
                ("tiny", "Tiny (39MB) - Fastest"),
                ("base", "Base (142MB) - Balanced"),
                ("small", "Small (466MB) - Good"),
                ("medium", "Medium (1.5GB) - Better"),
                ("large", "Large (3.1GB) - Best Accuracy"),
            ]

            for model_name, description in model_sizes:
                model_item = rumps.MenuItem(
                    description,
                    callback=lambda sender, model=model_name: self._select_model(model),
                )
                model_menu.add(model_item)

            provider_menu.add(model_menu)

        return provider_menu

    def _switch_provider(self, new_provider):
        """Switch to a different speech provider"""
        if self.is_recording:
            rumps.notification(
                "Termina",
                "Cannot Switch",
                "Please stop recording before switching providers",
            )
            return

        old_name = self.speech_provider.name if self.speech_provider else "None"
        self.speech_provider = new_provider

        # Update menu to reflect new selection
        self.provider_menu = self._create_provider_menu()
        self.audio_settings_menu = self._create_audio_settings_menu()
        self.menu = [
            self.start_item,
            rumps.separator,
            self.provider_menu,
            self.audio_settings_menu,
            rumps.separator,
            rumps.MenuItem("Hotkey: ⌘+Shift+V", callback=None),
            rumps.separator,
            rumps.MenuItem("Quit", callback=rumps.quit_application),
        ]

        rumps.notification(
            "Termina",
            "Provider Switched",
            f"Switched from {old_name} to {new_provider.name}",
        )
        print(f"Switched speech provider from {old_name} to {new_provider.name}")

    def _manage_models(self, _):
        """Show model management dialog"""
        # Build info message
        info_lines = ["Local Whisper Models:\n"]

        # Available openai-whisper models
        models = ["tiny", "base", "small", "medium", "large"]
        for model_name in models:
            info_lines.append(f"{model_name}: Auto-downloaded when first used")

        info_lines.append("\nModels are automatically downloaded and cached")
        info_lines.append("when first selected for use.\n")
        info_lines.append("Cache location: ~/.cache/whisper/")

        rumps.alert("Model Management", "\n".join(info_lines))

    def _select_model(self, model_name):
        """Select a specific model size for local whisper"""
        if self.is_recording:
            rumps.notification(
                "Termina",
                "Cannot Switch",
                "Please stop recording before changing model",
            )
            return

        # Update the WhisperCppProvider to use the selected model
        from speech_providers import WhisperCppProvider

        if isinstance(self.speech_provider, WhisperCppProvider):
            # Force reload with new model
            self.speech_provider._model = None
            self.speech_provider._model_name = None
            if self.speech_provider._load_model(model_name):
                rumps.notification(
                    "Termina", "Model Changed", f"Switched to {model_name} model"
                )
                print(f"Successfully switched to {model_name} model")
            else:
                rumps.notification(
                    "Termina", "Error", f"Failed to load {model_name} model"
                )
                print(f"Failed to load {model_name} model")
        else:
            rumps.notification(
                "Termina", "Error", "Please switch to Local Whisper provider first"
            )

    def _create_audio_settings_menu(self):
        """Create audio settings menu including noise reduction"""
        audio_menu = rumps.MenuItem("Audio Settings")

        # Get FFmpeg processor
        processor = get_processor()

        # Noise reduction toggle
        if processor.ffmpeg_available:
            noise_reduction_title = (
                "✓ Noise Reduction"
                if processor.noise_reduction_enabled
                else "○ Noise Reduction"
            )
            noise_reduction_item = rumps.MenuItem(
                noise_reduction_title, callback=self._toggle_noise_reduction
            )
            audio_menu.add(noise_reduction_item)

            # FFmpeg status
            ffmpeg_status = rumps.MenuItem("FFmpeg: Available ✓", callback=None)
            audio_menu.add(ffmpeg_status)

            # Advanced settings submenu
            advanced_menu = rumps.MenuItem("Advanced Filters")

            # Individual filter toggles
            for filter_name, filter_config in processor.filters.items():
                filter_title = f"{'✓' if filter_config['enabled'] else '○'} {filter_name.replace('_', ' ').title()}"
                filter_item = rumps.MenuItem(
                    filter_title,
                    callback=lambda sender, fn=filter_name: self._toggle_filter(fn),
                )
                advanced_menu.add(filter_item)

            audio_menu.add(rumps.separator)
            audio_menu.add(advanced_menu)
        else:
            # FFmpeg not available
            audio_menu.add(rumps.MenuItem("FFmpeg: Not Available ✗", callback=None))
            audio_menu.add(
                rumps.MenuItem("Install FFmpeg: brew install ffmpeg", callback=None)
            )

        return audio_menu

    def _toggle_noise_reduction(self, sender):
        """Toggle noise reduction on/off"""
        processor = get_processor()
        processor.set_noise_reduction(not processor.noise_reduction_enabled)

        # Update menu
        self.audio_settings_menu = self._create_audio_settings_menu()
        self._update_menu()

        status = "enabled" if processor.noise_reduction_enabled else "disabled"
        rumps.notification("Termina", "Noise Reduction", f"Noise reduction {status}")

    def _toggle_filter(self, filter_name):
        """Toggle individual audio filter"""
        processor = get_processor()
        current_state = processor.filters[filter_name]["enabled"]
        processor.configure_filter(filter_name, enabled=not current_state)

        # Update menu
        self.audio_settings_menu = self._create_audio_settings_menu()
        self._update_menu()

        status = "enabled" if not current_state else "disabled"
        rumps.notification(
            "Termina", f"{filter_name.replace('_', ' ').title()}", f"Filter {status}"
        )

    def _update_menu(self):
        """Update the main menu"""
        self.menu = [
            self.start_item,
            rumps.separator,
            self.provider_menu,
            self.audio_settings_menu,
            rumps.separator,
            rumps.MenuItem("Hotkey: ⌘+Shift+V", callback=None),
            rumps.separator,
            rumps.MenuItem("Quit", callback=rumps.quit_application),
        ]


def main():
    # Load environment variables from .env.local
    load_dotenv(".env.local")

    # Check if any speech provider is available
    from speech_providers import SpeechProviderFactory

    provider = SpeechProviderFactory.get_provider()
    if not provider:
        available_providers = SpeechProviderFactory.get_available_providers()
        if not available_providers:
            rumps.alert(
                "Termina Setup",
                "No speech recognition providers available.\n\n"
                "Please configure:\n"
                "• OpenAI API: Set OPENAI_API_KEY in .env.local\n"
                "• Local Whisper: Run 'uv add openai-whisper'",
            )
            return

    # Start the application
    app = TerminaApp()
    try:
        app.run()
    except KeyboardInterrupt:
        print("Application interrupted")
    finally:
        app.cleanup()


if __name__ == "__main__":
    main()
