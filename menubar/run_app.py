"""
Platform-agnostic launcher for Unscatter menubar/tray app.

Automatically detects the operating system and launches the appropriate app:
- macOS: menubar_app.py (using rumps)
- Windows: windows_app.py (using pystray)
"""

import platform
import sys

def main():
    system = platform.system()
    
    if system == "Darwin":
        # macOS
        try:
            from menubar_app import UnscatterApp
            print("Starting Unscatter menu bar app (macOS)...")
            app = UnscatterApp()
            app.run()
        except ImportError as e:
            print(f"Error: Could not import macOS app. Make sure 'rumps' is installed.")
            print(f"Install with: pip install rumps")
            print(f"Details: {e}")
            sys.exit(1)
            
    elif system == "Windows":
        # Windows
        try:
            from windows_app import UnscatterWindowsApp
            print("Starting Unscatter system tray app (Windows)...")
            app = UnscatterWindowsApp()
            app.run()
        except ImportError as e:
            print(f"Error: Could not import Windows app. Make sure required packages are installed.")
            print(f"Install with: pip install pystray pillow winotify")
            print(f"Details: {e}")
            sys.exit(1)
            
    else:
        print(f"Error: Unsupported operating system: {system}")
        print("Unscatter menubar app currently supports macOS and Windows only.")
        sys.exit(1)


if __name__ == "__main__":
    main()

# Made with Bob
