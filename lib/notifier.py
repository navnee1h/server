"""
Notifier - Sends desktop notifications via notify-send.
Silently skips if notify-send is not available (e.g. headless server).
"""

import subprocess
import shutil


def notify(title, message):
    """Send a desktop notification. Fails silently if not supported."""
    if shutil.which("notify-send"):
        try:
            subprocess.run(
                ["notify-send", title, message],
                capture_output=True,
                timeout=5
            )
        except Exception:
            pass  # Never crash the main flow for a notification
