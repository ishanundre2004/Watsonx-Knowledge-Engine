import os
import subprocess
import tempfile
import threading
import webbrowser
import tkinter as tk
from tkinter import simpledialog

import numpy as np
import pystray
from PIL import Image, ImageDraw
import sounddevice as sd
import soundfile as sf
import requests
from winotify import Notification, audio

BACKEND = "http://127.0.0.1:8000"
SAMPLE_RATE = 16000


def create_icon_image(color="blue"):
    """Create a simple icon image for the system tray."""
    width = 64
    height = 64
    image = Image.new('RGB', (width, height), color)
    dc = ImageDraw.Draw(image)
    # Draw a brain emoji-like circle
    dc.ellipse([10, 10, 54, 54], fill='white', outline=color)
    return image


class UnscatterWindowsApp:
    def __init__(self):
        self.recording = False
        self.audio_frames = []
        self.stream = None
        self.screen_recording = False
        self.screen_process = None
        self.screen_file = None
        self.icon = None
        
        # Create menu items
        self.voice_menu_item = pystray.MenuItem(
            "Start Voice Capture",
            self.toggle_voice
        )
        self.screen_menu_item = pystray.MenuItem(
            "Start Screen Recording",
            self.toggle_screen
        )
        
    def run(self):
        """Start the system tray app."""
        menu = pystray.Menu(
            self.voice_menu_item,
            self.screen_menu_item,
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Open Unscatter", self.open_web),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self.quit_app)
        )
        
        self.icon = pystray.Icon(
            "Unscatter",
            create_icon_image("blue"),
            "Unscatter",
            menu
        )
        
        self.icon.run()

    # ── Voice capture ──────────────────────────────────────────────────────────

    def toggle_voice(self, icon, item):
        if self.screen_recording:
            self._notify("Unscatter", "Stop screen recording first.")
            return
        if not self.recording:
            self.start_recording()
            # Update menu item text
            self.voice_menu_item = pystray.MenuItem(
                "⏺ Stop & Ingest Voice",
                self.toggle_voice
            )
            self._update_menu()
            self._update_icon("red")
        else:
            self.stop_and_ingest()
            # Update menu item text
            self.voice_menu_item = pystray.MenuItem(
                "Start Voice Capture",
                self.toggle_voice
            )
            self._update_menu()
            self._update_icon("blue")

    def start_recording(self):
        self.recording = True
        self.audio_frames = []

        def callback(indata, frames, time, status):
            self.audio_frames.append(indata.copy())

        self.stream = sd.InputStream(
            samplerate=SAMPLE_RATE, channels=1, callback=callback
        )
        self.stream.start()

    def stop_and_ingest(self):
        self.recording = False
        self.stream.stop()
        self.stream.close()

        if not self.audio_frames:
            self._notify("Unscatter", "No audio recorded.")
            return

        path = tempfile.mktemp(suffix=".wav")
        sf.write(path, np.concatenate(self.audio_frames, axis=0), SAMPLE_RATE)
        threading.Thread(
            target=self._send_to_backend, args=(path,), daemon=True
        ).start()

    def _send_to_backend(self, wav_path: str):
        try:
            with open(wav_path, "rb") as f:
                r = requests.post(
                    f"{BACKEND}/api/capture/voice", files={"file": f}, timeout=30
                )
            r.raise_for_status()
            transcript = r.json()["raw_text"]

            r = requests.post(
                f"{BACKEND}/api/ingest",
                json={"modality": "voice", "raw_text": transcript, "user_note": ""},
                timeout=60,
            )
            r.raise_for_status()
            summary = r.json().get("summary_for_user", "Captured.")
            self._notify("Unscatter", summary)
        except requests.exceptions.ConnectionError:
            self._notify("Unscatter", "Backend not running — start uvicorn first.")
        except Exception as e:
            self._notify("Unscatter", f"Capture failed: {e}")
        finally:
            try:
                os.unlink(wav_path)
            except OSError:
                pass

    # ── Screen recording ───────────────────────────────────────────────────────

    def toggle_screen(self, icon, item):
        if self.recording:
            self._notify("Unscatter", "Stop voice capture first.")
            return
        if not self.screen_recording:
            self._start_screen_recording()
        else:
            self._stop_screen_recording()

    def _start_screen_recording(self):
        # Check if ffmpeg is available
        try:
            subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            self._notify("Unscatter", "ffmpeg not found — install ffmpeg first")
            return

        self.screen_file = tempfile.mktemp(suffix=".mp4")
        
        # Windows screen recording using gdigrab
        cmd = [
            "ffmpeg",
            "-f", "gdigrab",
            "-framerate", "15",
            "-i", "desktop",
            "-vcodec", "libx264",
            "-preset", "ultrafast",
            "-y",
            self.screen_file,
        ]
        
        try:
            self.screen_process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except FileNotFoundError:
            self._notify("Unscatter", "ffmpeg not found — install ffmpeg first")
            return
            
        self.screen_recording = True
        self.screen_menu_item = pystray.MenuItem(
            "⏺ Stop Screen Recording",
            self.toggle_screen
        )
        self._update_menu()
        self._update_icon("orange")

    def _stop_screen_recording(self):
        self.screen_recording = False
        self.screen_menu_item = pystray.MenuItem(
            "Start Screen Recording",
            self.toggle_screen
        )
        self._update_menu()
        self._update_icon("blue")
        
        process = self.screen_process
        mp4_path = self.screen_file
        self.screen_process = None
        self.screen_file = None
        
        threading.Thread(
            target=self._process_screen_recording,
            args=(process, mp4_path),
            daemon=True,
        ).start()

    def _process_screen_recording(self, process, mp4_path: str):
        wav_path = None
        try:
            # Stop ffmpeg cleanly so the container is finalized
            try:
                process.stdin.write(b"q\n")
                process.stdin.flush()
                process.wait(timeout=15)
            except Exception:
                process.kill()
                process.wait()

            # Ask for context before the transcription round-trip
            context = self._ask_context()
            if context is None:
                self._notify("Unscatter", "Screen recording cancelled.")
                return

            # Extract audio track from the video (best-effort — silent/missing audio is fine)
            transcript = ""
            wav_path = tempfile.mktemp(suffix=".wav")
            extract = subprocess.run(
                [
                    "ffmpeg", "-i", mp4_path,
                    "-vn", "-acodec", "pcm_s16le",
                    "-ar", "16000", "-ac", "1",
                    "-y", wav_path,
                ],
                capture_output=True,
            )
            if extract.returncode == 0:
                try:
                    with open(wav_path, "rb") as f:
                        r = requests.post(
                            f"{BACKEND}/api/capture/voice", files={"file": f}, timeout=30
                        )
                    r.raise_for_status()
                    transcript = r.json().get("raw_text", "").strip()
                except Exception:
                    pass  # transcription failure is non-fatal

            raw_text = transcript or "(no speech — context only)"
            r = requests.post(
                f"{BACKEND}/api/ingest",
                json={"modality": "screen", "raw_text": raw_text, "user_note": context},
                timeout=60,
            )
            r.raise_for_status()
            summary = r.json().get("summary_for_user", "Captured.")
            self._notify("Unscatter", summary)

        except requests.exceptions.ConnectionError:
            self._notify("Unscatter", "Backend not running — start uvicorn first.")
        except Exception as e:
            self._notify("Unscatter", f"Screen capture failed: {e}")
        finally:
            for path in filter(None, [mp4_path, wav_path]):
                try:
                    os.unlink(path)
                except OSError:
                    pass

    def _ask_context(self) -> str | None:
        """Show a tkinter dialog to get context. Returns the text, or None if cancelled."""
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        result = simpledialog.askstring(
            "Unscatter",
            "WHAT IS THE CONTEXT OF THIS SCREEN RECORDING?",
            parent=root
        )
        
        root.destroy()
        return result if result is not None else None

    # ── Shared helpers ─────────────────────────────────────────────────────────

    def _notify(self, title: str, message: str):
        """Show a Windows notification."""
        try:
            toast = Notification(
                app_id="Unscatter",
                title=title,
                msg=message,
                duration="short"
            )
            toast.set_audio(audio.Default, loop=False)
            toast.show()
        except Exception:
            # Fallback if winotify fails
            print(f"{title}: {message}")

    def open_web(self, icon, item):
        """Open the Unscatter web interface."""
        webbrowser.open("http://localhost:5173")

    def quit_app(self, icon, item):
        """Quit the application."""
        if self.recording:
            self.stream.stop()
            self.stream.close()
        if self.screen_recording and self.screen_process:
            self.screen_process.kill()
        icon.stop()

    def _update_menu(self):
        """Update the menu with new items."""
        if self.icon:
            menu = pystray.Menu(
                self.voice_menu_item,
                self.screen_menu_item,
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Open Unscatter", self.open_web),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Quit", self.quit_app)
            )
            self.icon.menu = menu
            self.icon.update_menu()

    def _update_icon(self, color):
        """Update the tray icon color."""
        if self.icon:
            self.icon.icon = create_icon_image(color)


if __name__ == "__main__":
    UnscatterWindowsApp().run()

# Made with Bob
