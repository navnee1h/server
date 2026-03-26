"""
Dependency Checker - Verifies all required system tools are installed
before any transfer is attempted.
"""

import shutil
import sys

REQUIRED_TOOLS = {
    "scp":          "OpenSSH client  →  sudo apt install openssh-client",
    "ssh":          "OpenSSH client  →  sudo apt install openssh-client",
    "sshpass":      "sshpass         →  sudo apt install sshpass",
    "zip":          "zip             →  sudo apt install zip",
    "unzip":        "unzip           →  sudo apt install unzip",
}

OPTIONAL_TOOLS = {
    "notify-send":  "libnotify-bin   →  sudo apt install libnotify-bin  (for desktop notifications)",
    "tqdm":         "Python tqdm     →  pip install tqdm                (for progress bar)",
}


def check_dependencies():
    """Check required tools. Print warnings for optional ones. Exit if required ones missing."""
    missing_required = []

    for tool, install_hint in REQUIRED_TOOLS.items():
        if shutil.which(tool) is None:
            missing_required.append((tool, install_hint))

    if missing_required:
        print("❌  Missing required dependencies:\n")
        for tool, hint in missing_required:
            print(f"    {tool:<15}  Install: {hint}")
        print()
        sys.exit(1)

    # Check optional tools and warn (don't exit)
    for tool, install_hint in OPTIONAL_TOOLS.items():
        if tool == "tqdm":
            try:
                import tqdm  # noqa
            except ImportError:
                print(f"⚠️   Optional: {install_hint}")
        elif shutil.which(tool) is None:
            print(f"⚠️   Optional: {install_hint}")
