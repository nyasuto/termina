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
        self.is_recording = False
        self.audio_data = None
        self.recording_thread = None
        self.recording_start_time = None
        
        # Menu items
        self.start_item = rumps.MenuItem("Start Recording", callback=self.toggle_recording)
        self.menu = [
            self.start_item,
            rumps.separator,
            rumps.MenuItem("Quit", callback=rumps.quit_application)
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
        rumps.notification("WhisperTerm", "Recording Started", "Recording... Click 'Stop Recording' to finish")
        
        # Start recording in a separate thread
        self.recording_thread = threading.Thread(target=self._start_continuous_recording)
        self.recording_thread.daemon = True
        self.recording_thread.start()
    
    def stop_recording(self):
        """Stop audio recording and process"""
        if not self.is_recording:
            return
            
        self.is_recording = False
        self.start_item.title = "Start Recording"
        rumps.notification("WhisperTerm", "Recording Stopped", "Processing audio...")
        
        # Stop the recording
        sd.stop()
        
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
                dtype='int16'
            )
        except Exception as e:
            rumps.notification("WhisperTerm", "Error", f"Recording failed: {str(e)}")
            self.is_recording = False
            self.start_item.title = "Start Recording"
    
    def _process_audio(self):
        """Process the recorded audio"""
        try:
            import time
            print("Starting audio processing...")
            
            if self.audio_data is None:
                print("Error: No audio data to process")
                rumps.notification("WhisperTerm", "Error", "No audio data to process")
                return
            
            print(f"Audio data shape: {self.audio_data.shape if hasattr(self.audio_data, 'shape') else 'No shape attribute'}")
            
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
            
            print(f"Final audio data shape: {audio_data.shape if hasattr(audio_data, 'shape') else 'No shape attribute'}")
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_path = temp_file.name
                print(f"Saving audio to temporary file: {temp_path}")
                wavfile.write(temp_path, self.sample_rate, audio_data)
                print(f"Audio file saved successfully")
            
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
                rumps.notification("WhisperTerm", "Text Pasted", f"Pasted: {transcription}")
                print("Text pasted successfully")
            else:
                print("No transcription result received")
                rumps.notification("WhisperTerm", "Error", "Failed to transcribe audio")
                
        except Exception as e:
            print(f"Processing failed with error: {str(e)}")
            import traceback
            traceback.print_exc()
            rumps.notification("WhisperTerm", "Error", f"Processing failed: {str(e)}")
        finally:
            self.audio_data = None
            self.recording_start_time = None
            print("Audio processing completed")

    def _transcribe_audio(self, audio_path):
        """Transcribe audio using OpenAI Whisper API"""
        try:
            print(f"Starting transcription for file: {audio_path}")
            
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
                print(f"Transcription successful: '{result_text}'")
                return result_text
                
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
            applescript = f'''
            set the clipboard to "{text}"
            tell application "System Events"
                keystroke "v" using command down
            end tell
            '''
            
            print("Executing AppleScript...")
            result = subprocess.run(['osascript', '-e', applescript], 
                                  capture_output=True, text=True, check=True)
            print(f"AppleScript executed successfully: {result}")
            
        except subprocess.CalledProcessError as e:
            print(f"AppleScript error: {e}")
            print(f"Error output: {e.stderr if hasattr(e, 'stderr') else 'No stderr'}")
            rumps.notification("WhisperTerm", "Error", "Failed to paste text")
        except Exception as e:
            print(f"Unexpected error in paste_text: {e}")
            import traceback
            traceback.print_exc()
            rumps.notification("WhisperTerm", "Error", f"Paste failed: {str(e)}")


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