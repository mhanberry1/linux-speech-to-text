# Linux Speech-to-Text Tool

A simple Linux application that converts speech to text using OpenAI's Whisper model. The app is triggered by keyboard shortcuts, provides visual feedback during recording and processing, and automatically pastes the transcribed text.

## Features

- Start/stop recording with Alt+R (no time limit)
- Visual indicator showing recording status and elapsed time
- Processing indicator with animated feedback
- Automatic clipboard paste of transcribed text
- Uses OpenAI's Whisper model for accurate speech recognition
- Systemd service for automatic startup

## Requirements

- Python 3.7+
- PortAudio (for audio recording)
- X11 (for Linux desktop integration)

## Installation

1. Install PortAudio (on Ubuntu/Debian):
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the script:
```bash
./launch.sh
```
Or manually:
```bash
python speech_to_text.py
```

2. Press `Alt+R` to start recording
3. Speak clearly into your microphone
4. Press `Alt+R` again to stop recording
5. Wait for processing (a visual indicator will show progress)
6. The transcribed text will be automatically pasted at your cursor location
7. Press `Ctrl+C` in the terminal to exit

Note: The first run will download the Whisper base model.

## Running on Startup

To have the script start automatically when you log in:

1. Create the systemd user service directory and file:
```bash
mkdir -p ~/.config/systemd/user/
```

2. Create the service file at `~/.config/systemd/user/speech-to-text.service`:
```ini
[Unit]
Description=Speech to Text Service
After=graphical-session.target
PartOf=graphical-session.target

[Service]
Type=simple
Environment=DISPLAY=:0
Environment=XAUTHORITY=%h/.Xauthority
ExecStart=/home/rhotate/Dev/linux-speech-to-text/launch.sh
Restart=on-failure
RestartSec=5

[Install]
WantedBy=graphical-session.target
```

3. Enable and start the service:
```bash
# Reload systemd to recognize the new service
systemctl --user daemon-reload

# Enable the service to start on login
systemctl --user enable speech-to-text

# Start the service now
systemctl --user start speech-to-text
```

4. Check the status:
```bash
# View status
systemctl --user status speech-to-text

# View logs
journalctl --user -u speech-to-text
```

## Dependencies

- whisper: OpenAI's speech recognition model
- sounddevice: Audio recording
- pynput: Keyboard event handling
- pyperclip: Clipboard management
- tkinter: GUI for recording indicator

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.
