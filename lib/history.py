"""
History Logger - Records all transfer attempts to ~/.server_history.log
"""

import os
from datetime import datetime

HISTORY_PATH = os.path.expanduser("~/.server_history.log")
DEFAULT_SHOW_COUNT = 10


class HistoryLogger:
    def append(self, status, filename, destination):
        """Append a transfer record to the log file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        line = f"[{timestamp}] {status:<8} {filename} → {destination}\n"
        with open(HISTORY_PATH, "a") as f:
            f.write(line)

    def show(self, show_all=False):
        """Display transfer history."""
        if not os.path.exists(HISTORY_PATH):
            print("📭  No transfer history yet.")
            return

        with open(HISTORY_PATH, "r") as f:
            lines = f.readlines()

        if not lines:
            print("📭  No transfer history yet.")
            return

        if not show_all:
            lines = lines[-DEFAULT_SHOW_COUNT:]
            header = f"📋  Last {min(DEFAULT_SHOW_COUNT, len(lines))} transfers  (use 'server history all' for full log)"
        else:
            header = f"📋  All transfers ({len(lines)} records)"

        print()
        print(header)
        print("─" * 70)
        for line in lines:
            line = line.rstrip()
            if "SUCCESS" in line:
                print(f"  ✅  {line}")
            elif "FAILED" in line:
                print(f"  ❌  {line}")
            else:
                print(f"      {line}")
        print("─" * 70)
        print(f"  Log file: {HISTORY_PATH}\n")
