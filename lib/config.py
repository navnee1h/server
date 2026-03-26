"""
Config Manager - Loads, saves, validates, and displays configuration.
"""

import json
import os
import re

CONFIG_PATH = os.path.expanduser("~/.server_config.json")

DEFAULT_CONFIG = {
    "host": "",
    "username": "",
    "password": "",
    "destination": "/home/server/Downloads",
    "port": 22,
    "zip_threshold_mb": 50
}

VALID_KEYS = list(DEFAULT_CONFIG.keys())


class ConfigManager:
    def __init__(self):
        self.config = self._load()

    def _load(self):
        if not os.path.exists(CONFIG_PATH):
            self._save(DEFAULT_CONFIG)
            print(f"⚙️  New config created at {CONFIG_PATH}")
            print("    Run: server edit host <ip>  to get started.\n")
            return dict(DEFAULT_CONFIG)
        with open(CONFIG_PATH, "r") as f:
            data = json.load(f)
        # Fill in any missing keys with defaults
        for k, v in DEFAULT_CONFIG.items():
            data.setdefault(k, v)
        return data

    def _save(self, data):
        with open(CONFIG_PATH, "w") as f:
            json.dump(data, f, indent=2)

    def get(self, key):
        return self.config.get(key)

    def show(self):
        print("\n⚙️  Current Server Configuration")
        print("─" * 40)
        for key, val in self.config.items():
            display_val = "********" if key == "password" and val else val
            print(f"  {key:<20} {display_val}")
        print("─" * 40)
        print(f"  Config file: {CONFIG_PATH}\n")

    def edit(self, key, value):
        if key not in VALID_KEYS:
            print(f"❌  Unknown key: '{key}'")
            print(f"    Valid keys: {', '.join(VALID_KEYS)}")
            return

        # Validate
        error = self._validate(key, value)
        if error:
            print(f"❌  {error}")
            return

        # Cast types
        if key == "port":
            value = int(value)
        elif key == "zip_threshold_mb":
            value = int(value)

        self.config[key] = value
        self._save(self.config)
        display_val = "********" if key == "password" else value
        print(f"✅  Updated: {key} = {display_val}")

    def _validate(self, key, value):
        if key == "host":
            if not value.strip():
                return "Host cannot be empty."
        elif key == "port":
            if not value.isdigit() or not (1 <= int(value) <= 65535):
                return "Port must be a number between 1 and 65535."
        elif key == "zip_threshold_mb":
            if not value.isdigit() or int(value) <= 0:
                return "zip_threshold_mb must be a positive integer."
        elif key == "destination":
            if not value.startswith("/"):
                return "Destination must be an absolute path (starts with /)."
        return None

    def validate_for_transfer(self):
        """Check required fields before a transfer."""
        missing = []
        for key in ("host", "username", "password", "destination"):
            if not self.config.get(key, "").strip():
                missing.append(key)
        if missing:
            print("❌  Missing required config values:")
            for k in missing:
                print(f"    server edit {k} <value>")
            return False
        return True
