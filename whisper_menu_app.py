#!/usr/bin/env python3
"""
WhisperTerm - macOS Menu Bar Voice Command Application
Records audio, transcribes with OpenAI Whisper, and executes commands in Terminal
"""

import os
import tempfile
import subprocess
import threading
import rumps
import sounddevice as sd
import scipy.io.wavfile as wavfile
from openai import OpenAI
from dotenv import load_dotenv


class WhisperTermApp(rumps.App):
    def __init__(self):
        super(WhisperTermApp, self).__init__("🎤", quit_button=None)
        
        # Load environment variables from .env.local
        load_dotenv('.env.local')
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Recording settings
        self.sample_rate = 44100
        self.recording_duration = 5  # seconds
        self.is_recording = False
        
        # Menu items
        self.menu = [
            rumps.MenuItem("Start Recording", callback=self.start_recording),
            rumps.separator,
            rumps.MenuItem("Quit", callback=rumps.quit_application)
        ]

    def start_recording(self, _):
        """Start audio recording in a separate thread"""
        if self.is_recording:
            rumps.notification("WhisperTerm", "Recording", "Already recording...")
            return
            
        self.is_recording = True
        thread = threading.Thread(target=self._record_and_process)
        thread.daemon = True
        thread.start()

    def _record_and_process(self):
        """Record audio, transcribe, and execute command"""
        try:
            # Show recording notification
            rumps.notification("WhisperTerm", "Recording", f"Recording for {self.recording_duration} seconds...")
            
            # Record audio
            audio_data = sd.rec(
                int(self.recording_duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1,
                dtype='int16'
            )
            sd.wait()  # Wait for recording to complete
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_path = temp_file.name
                wavfile.write(temp_path, self.sample_rate, audio_data)
            
            # Transcribe with Whisper
            transcription = self._transcribe_audio(temp_path)
            
            # Clean up temporary file
            os.unlink(temp_path)
            
            if transcription:
                # Send command to Terminal
                self._send_to_terminal(transcription)
                rumps.notification("WhisperTerm", "Command Executed", f"Sent: {transcription}")
            else:
                rumps.notification("WhisperTerm", "Error", "Failed to transcribe audio")
                
        except Exception as e:
            rumps.notification("WhisperTerm", "Error", f"Recording failed: {str(e)}")
        finally:
            self.is_recording = False

    def _transcribe_audio(self, audio_path):
        """Transcribe audio using OpenAI Whisper API"""
        try:
            with open(audio_path, 'rb') as audio_file:
                transcription = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="en"  # Can be changed to "ja" for Japanese
                )
                return transcription.text.strip()
        except Exception as e:
            print(f"Transcription error: {e}")
            return None

    def _send_to_terminal(self, command):
        """Send command to Terminal using AppleScript"""
        try:
            applescript = f'''
            tell application "Terminal"
                activate
                do script "{command}"
            end tell
            '''
            subprocess.run(['osascript', '-e', applescript], check=True)
        except subprocess.CalledProcessError as e:
            print(f"AppleScript error: {e}")
            rumps.notification("WhisperTerm", "Error", "Failed to send command to Terminal")


def main():
    # Load environment variables from .env.local
    load_dotenv('.env.local')
    
    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        rumps.alert("WhisperTerm Setup", "Please create a .env.local file with your OPENAI_API_KEY")
        return
    
    # Start the application
    app = WhisperTermApp()
    app.run()


if __name__ == "__main__":
    main()