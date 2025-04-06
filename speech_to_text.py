import sounddevice as sd
import numpy as np
import whisper
from pynput import keyboard
from pynput.keyboard import Key, Controller
import pyperclip
import tempfile
import wave
import os
import threading
import time
import tkinter as tk
from tkinter import ttk

# Initialize keyboard controller for pasting
keyboard_controller = Controller()

# Global flags and variables
recording_active = False
alt_pressed = False
recording_window = None

def on_press(key):
    global alt_pressed, recording_active
    try:
        # Check for alt+r to toggle recording
        if key == keyboard.Key.alt_l:
            alt_pressed = True
        elif hasattr(key, 'char') and key.char == 'r' and alt_pressed:
            if recording_active:
                print("Stopping recording...")
                recording_active = False
            else:
                recording_active = True
    except AttributeError:
        pass

def on_release(key):
    global alt_pressed
    if key == keyboard.Key.alt_l:
        alt_pressed = False

def update_indicator(text, is_processing=False):
    """Update the indicator window with text."""
    global recording_window
    if recording_window and hasattr(recording_window, 'label'):
        if is_processing:
            # Use a sequence of dots for animation
            dots = '.' * (int(time.time() * 2) % 4)
            recording_window.label.config(text=f'⚙️ {text}{dots}')
        else:
            recording_window.label.config(text=text)
        recording_window.update()



def update_recording_indicator(elapsed_seconds):
    """Update the recording indicator with elapsed time."""
    update_indicator(f'🎤 Recording... {elapsed_seconds}s')



def show_indicator(initial_text=''):
    """Show an indicator window at the top center of the screen."""
    global recording_window
    
    if recording_window is None:
        recording_window = tk.Tk()
        recording_window.title("")
        
        # Remove window decorations and make it stay on top
        recording_window.overrideredirect(True)
        recording_window.attributes('-topmost', True)
        
        # Calculate position (top center)
        screen_width = recording_window.winfo_screenwidth()
        window_width = 300  # Made wider for processing text
        window_height = 50
        x_position = (screen_width - window_width) // 2
        
        # Configure window
        recording_window.geometry(f'{window_width}x{window_height}+{x_position}+0')
        recording_window.configure(bg='black')
        
        # Create a frame with padding for better appearance
        frame = tk.Frame(recording_window, bg='black', padx=10, pady=5)
        frame.pack(fill="both", expand=True)
        
        # Add indicator label
        label = tk.Label(
            frame,
            text=initial_text,
            font=('Arial', 14),
            fg='white',
            bg='black',
            padx=10,
            pady=5
        )
        label.pack(expand=True)
        recording_window.label = label
        
        # Set window to be 70% transparent
        recording_window.wait_visibility()
        recording_window.attributes('-alpha', 0.7)
    else:
        update_indicator(initial_text)
    
    recording_window.update()

def hide_recording_indicator():
    """Hide the recording indicator window."""
    global recording_window
    if recording_window:
        recording_window.destroy()
        recording_window = None

def record_audio(duration=60, sample_rate=44100):
    """Record audio until stopped with Alt+R."""
    global recording_active
    
    print("Recording... (Press Alt+R again to stop)")
    show_indicator('🎤 Recording... 0s')
    recording_active = True
    
    # Start recording
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
    
    # Wait for completion or stop command
    start_time = time.time()
    
    try:
        while sd.get_stream().active and recording_active:
            elapsed = int(time.time() - start_time)
            update_recording_indicator(elapsed)
            time.sleep(0.1)
            
        print("Recording stopped")
        sd.stop()
    except Exception as e:
        print(f"Error during recording: {e}")
        sd.stop()
        hide_recording_indicator()
        recording_active = False
        raise
    
    recorded_duration = time.time() - start_time
    return recording[:int(recorded_duration * sample_rate)]

def save_audio(recording, sample_rate=44100):
    """Save recording to a temporary WAV file."""
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        with wave.open(f.name, 'wb') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            wav.writeframes((recording * 32767).astype(np.int16).tobytes())
        return f.name

def transcribe_audio(audio_file):
    """Transcribe audio file to text using Whisper."""
    result = model.transcribe(audio_file)
    return result["text"].strip()

def main():
    print("Speech-to-Text Tool")
    print("Press Alt+R to start/stop recording")
    print("Press Ctrl+C to exit")
    
    global model
    model = whisper.load_model("base")  # Load model once at startup
    
    # Create a hidden root window to handle Tk events
    root = tk.Tk()
    root.withdraw()
    
    # Initialize keyboard listener
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    
    try:
        while True:
            if recording_active:
                try:
                    recording = record_audio()
                    if len(recording) > 0:  # Only process if we have recorded something
                        print("Processing...")
                        update_indicator("Converting speech to text", is_processing=True)
                        
                        audio_file = save_audio(recording)
                        text = transcribe_audio(audio_file)
                        os.unlink(audio_file)  # Clean up temp file
                        
                        update_indicator("Pasting text...", is_processing=True)
                        pyperclip.copy(text)
                        print(f"Transcribed and copied to clipboard: {text}")
                        
                        # Simulate Ctrl+V to paste the text
                        time.sleep(0.5)  # Small delay to ensure copy is complete
                        keyboard_controller.press(Key.ctrl)
                        keyboard_controller.press('v')
                        keyboard_controller.release('v')
                        keyboard_controller.release(Key.ctrl)
                        
                        # Show success message briefly
                        update_indicator("✓ Done!")
                        time.sleep(1)
                        hide_recording_indicator()
                except Exception as e:
                    print(f"Error: {str(e)}")
            
            root.update()  # Process any pending Tk events
            time.sleep(0.1)  # Prevent high CPU usage
            
    except KeyboardInterrupt:
        print("\nExiting...")
        listener.stop()
        hide_recording_indicator()
        root.destroy()

if __name__ == "__main__":
    main()
