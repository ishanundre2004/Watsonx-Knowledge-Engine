# Unscatter System Tray / Menu Bar App

Cross-platform companion app that lets you capture knowledge from any app without opening the browser.

**Supported Platforms:**
- macOS (Menu Bar App)
- Windows (System Tray App)

## Prerequisites

### macOS
- Python 3.8+
- macOS 10.14 or later

### Windows
- Python 3.8+
- Windows 10 or later
- [FFmpeg](https://ffmpeg.org/download.html) installed and added to PATH
  - Download from: https://www.gyan.dev/ffmpeg/builds/
  - Extract and add the `bin` folder to your system PATH

## Setup

```bash
# From the project root, using the same venv as the backend:
pip install -r menubar/requirements.txt

# Or create a separate env:
# macOS/Linux:
python3 -m venv menubar/venv
source menubar/venv/bin/activate
pip install -r menubar/requirements.txt

# Windows:
python -m venv menubar\venv
menubar\venv\Scripts\activate
pip install -r menubar/requirements.txt
```

## Run

Start the backend first, then:

```bash
# Cross-platform launcher (automatically detects your OS):
python menubar/run_app.py

# Or run platform-specific version directly:
# macOS only:
python menubar/menubar_app.py

# Windows only:
python menubar/windows_app.py
```

### macOS
A 🧠 icon appears in your menu bar (top-right corner).

### Windows
A 🧠 icon appears in your system tray (bottom-right corner, near the clock).

## Usage

### Voice Capture
1. Click 🧠 → **Start Voice Capture** — icon turns 🔴
2. Speak freely for as long as you want
3. Click 🔴 → **Stop & Ingest**
4. A notification appears with a summary of what was added to your brain
5. Open the web app to browse the new note

### Screen Recording
1. Click 🧠 → **Start Screen Recording** — icon turns 🔴
2. Your entire screen is being recorded
3. Click 🔴 → **Stop & Ingest**
4. Optionally add context about what you recorded
5. A notification appears when processing is complete

### Quick Actions
- **Open Web App** — Opens Unscatter in your default browser
- **Quit** — Closes the app

## Permissions

### macOS
First run: macOS will ask for **Microphone** access. Grant it.  
No Accessibility permission needed. No Karabiner. No keyboard remapping.

### Windows
First run: Windows may ask for **Microphone** access. Grant it.  
For screen recording, ensure FFmpeg is properly installed and in your PATH.

## Troubleshooting

### Windows: "FFmpeg not found"
- Download FFmpeg from https://www.gyan.dev/ffmpeg/builds/
- Extract the archive
- Add the `bin` folder to your system PATH
- Restart the terminal/app

### Windows: System tray icon not visible
- Check the hidden icons area (click the ^ arrow in the system tray)
- The app may be running in the background

### macOS: Menu bar icon not visible
- Check if the icon is hidden due to too many menu bar items
- Try using a menu bar management tool like Bartender

### Backend connection issues
- Ensure the backend is running on `http://localhost:8000`
- Check that no firewall is blocking the connection
- Verify the backend is accessible by opening http://localhost:8000 in your browser
