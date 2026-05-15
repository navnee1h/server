"""
CLI Parser - Routes user commands to appropriate handlers.
"""

import sys
from config import ConfigManager
from transfer import TransferEngine
from history import HistoryLogger
from dependency import check_dependencies


HELP_TEXT = """
╔══════════════════════════════════════════════════════╗
║                s2s CLI Tool                          ║
╚══════════════════════════════════════════════════════╝

Usage:
  s2s <path>               Send file or folder to server
  s2s show                 Show current configuration
  s2s edit <key> <value>   Edit a configuration value
  s2s history              Show last 10 transfer records
  s2s history all          Show all transfer records
  s2s help                 Show this help menu

Examples:
  s2s /home/nav/file.txt
  s2s /home/nav/project/
  s2s edit host 192.168.1.10
  s2s edit destination /home/s2s/Desktop
  s2s history

Editable config keys:
  host              Remote server IP or hostname
  username          SSH username
  password          SSH password
  destination       Remote destination path
  port              SSH port (default: 22)
  zip_threshold_mb  Folder size threshold for zipping (default: 50)

Notes:
  - Press ENTER to confirm transfers
  - Large folders are automatically zipped before sending
  - Zipped files are auto-extracted on the server
  - Logs are saved to ~/.s2s/history.log
"""


def run_cli():
    args = sys.argv[1:]

    # No arguments → show help
    if not args:
        print(HELP_TEXT)
        return

    command = args[0]

    # Help commands
    if command in ("help", "--help", "-h"):
        print(HELP_TEXT)
        return

    # Show config
    if command == "show":
        cfg = ConfigManager()
        cfg.show()
        return

    # Edit config
    if command == "edit":
        if len(args) < 3:
            print("❌  Usage: s2s edit <key> <value>")
            print("    Example: s2s edit host 192.168.1.10")
            sys.exit(1)
        key = args[1]
        value = " ".join(args[2:])
        cfg = ConfigManager()
        cfg.edit(key, value)
        return

    # History
    if command == "history":
        logger = HistoryLogger()
        show_all = len(args) > 1 and args[1] == "all"
        logger.show(show_all=show_all)
        return

    # Transfer (treat command as a path)
    path = command
    check_dependencies()
    cfg = ConfigManager()
    engine = TransferEngine(cfg)
    engine.transfer(path)
