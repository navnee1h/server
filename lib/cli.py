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
║              Server CLI Tool                         ║
╚══════════════════════════════════════════════════════╝

Usage:
  server <path>               Send file or folder to server
  server show                 Show current server configuration
  server edit <key> <value>   Edit a configuration value
  server history              Show last 10 transfer records
  server history all          Show all transfer records
  server help                 Show this help menu

Examples:
  server /home/nav/file.txt
  server /home/nav/project/
  server edit host 192.168.1.10
  server edit destination /home/server/Desktop
  server history

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
  - Logs are saved to ~/.server_history.log
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
            print("❌  Usage: server edit <key> <value>")
            print("    Example: server edit host 192.168.1.10")
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
