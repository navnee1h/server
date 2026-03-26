"""
Transfer Engine - Handles file/folder detection, compression, SCP transfer,
remote extraction, progress tracking, and cleanup.
"""

import os
import sys
import shutil
import subprocess
import zipfile
import threading
import time

from history import HistoryLogger
from notifier import notify
from progress import run_progress_bar

TMP_DIR = "/tmp/server_uploads"


class TransferEngine:
    def __init__(self, config):
        self.cfg = config
        self.logger = HistoryLogger()

    def transfer(self, path):
        path = os.path.expanduser(path.rstrip("/"))

        # --- Validate path ---
        if not os.path.exists(path):
            print(f"❌  File not found: {path}")
            sys.exit(1)

        if not self.cfg.validate_for_transfer():
            sys.exit(1)

        is_dir = os.path.isdir(path)
        name = os.path.basename(path)
        size_bytes = self._get_size(path)
        size_str = self._fmt_size(size_bytes)

        host = self.cfg.get("host")
        destination = self.cfg.get("destination")
        username = self.cfg.get("username")
        password = self.cfg.get("password")
        port = str(self.cfg.get("port") or 22)
        threshold_mb = int(self.cfg.get("zip_threshold_mb") or 50)

        # --- Confirmation prompt ---
        kind = "folder" if is_dir else "file"
        print(f"\n📤  Ready to send {kind}:")
        print(f"    {path}  ({size_str})")
        print(f"    → {username}@{host}:{destination}")
        print()
        print("    Press ENTER to continue or any other key + ENTER to cancel...")

        user_input = input()
        if user_input != "":
            print("🚫  Transfer cancelled.")
            return

        # --- Decide what to send ---
        os.makedirs(TMP_DIR, exist_ok=True)
        zip_path = None
        remote_file = name
        local_file = path

        if is_dir:
            size_mb = size_bytes / (1024 * 1024)
            if size_mb >= threshold_mb:
                print(f"📦  Folder is {size_str}, zipping before transfer...")
                zip_path = os.path.join(TMP_DIR, f"{name}.zip")
                self._zip_folder(path, zip_path)
                local_file = zip_path
                remote_file = f"{name}.zip"
                print(f"✅  Zipped to: {zip_path}  ({self._fmt_size(os.path.getsize(zip_path))})")
            else:
                # Send folder directly via scp -r
                pass

        # --- SCP Transfer with progress ---
        print()
        success = self._scp_transfer(
            local_file=local_file,
            remote_file=remote_file,
            username=username,
            password=password,
            host=host,
            port=port,
            destination=destination,
            is_dir=is_dir and zip_path is None,
            total_bytes=os.path.getsize(local_file) if not (is_dir and zip_path is None) else size_bytes,
        )

        if success and zip_path:
            # --- Remote unzip ---
            print(f"\n📂  Extracting on server...")
            unzip_ok = self._remote_unzip(username, password, host, port, destination, remote_file)
            if unzip_ok:
                print(f"✅  Extracted successfully on server.")
            else:
                print(f"⚠️   Remote extraction failed. Zip file left on server.")

        # --- Cleanup ---
        if zip_path:
            if success:
                os.remove(zip_path)
            else:
                print(f"⚠️   Kept local zip at {zip_path} for retry.")

        # --- Log & Notify ---
        status = "SUCCESS" if success else "FAILED"
        display_name = remote_file if zip_path else name
        self.logger.append(status, display_name, destination)

        if success:
            print(f"\n✅  Transfer complete: {name} → {destination}\n")
            notify("Transfer Complete", f"{name} uploaded successfully")
        else:
            print(f"\n❌  Transfer failed. Check logs: server history\n")
            notify("Transfer Failed", "Check logs for details")

    # ─────────────────────────────────────────────
    # Internal helpers
    # ─────────────────────────────────────────────

    def _scp_transfer(self, local_file, remote_file, username, password,
                      host, port, destination, is_dir, total_bytes):
        """Run scp with live progress bar via tqdm."""
        target = f"{username}@{host}:{destination}/"

        cmd = [
            "sshpass", f"-p{password}",
            "scp",
            "-P", port,
            "-o", "StrictHostKeyChecking=no",
            "-o", "ConnectTimeout=10",
        ]

        if is_dir:
            cmd += ["-r", local_file]
        else:
            cmd += [local_file]

        cmd.append(target)

        print(f"🚀  Uploading: {os.path.basename(local_file)}")

        try:
            success = run_progress_bar(cmd, total_bytes, os.path.basename(local_file))
            return success
        except FileNotFoundError:
            print("❌  sshpass or scp not found. Run the install script.")
            return False

    def _remote_unzip(self, username, password, host, port, destination, zip_name):
        """SSH into server and unzip the uploaded file."""
        remote_cmd = f"cd {destination} && unzip -o {zip_name} && rm -f {zip_name}"
        cmd = [
            "sshpass", f"-p{password}",
            "ssh",
            "-p", port,
            "-o", "StrictHostKeyChecking=no",
            "-o", "ConnectTimeout=10",
            f"{username}@{host}",
            remote_cmd
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0

    def _zip_folder(self, folder_path, zip_path):
        """Zip a folder into zip_path."""
        base = os.path.basename(folder_path)
        parent = os.path.dirname(folder_path)
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    abs_path = os.path.join(root, file)
                    arcname = os.path.relpath(abs_path, parent)
                    zf.write(abs_path, arcname)

    def _get_size(self, path):
        """Get total size in bytes of file or folder."""
        if os.path.isfile(path):
            return os.path.getsize(path)
        total = 0
        for root, dirs, files in os.walk(path):
            for f in files:
                try:
                    total += os.path.getsize(os.path.join(root, f))
                except OSError:
                    pass
        return total

    def _fmt_size(self, size_bytes):
        """Human-readable file size."""
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
