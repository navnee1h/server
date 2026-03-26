"""
Progress Tracker - Displays real-time upload progress using tqdm.

Strategy: We run scp in a subprocess, monitor the local temp file size
shrink or use pv if available. Since scp doesn't expose byte progress
directly, we use a size-polling approach on Linux via /proc or fallback
to a time-based spinner with tqdm.
"""

import subprocess
import threading
import time
import os
import sys

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False


def run_progress_bar(cmd, total_bytes, filename):
    """
    Runs scp command and shows a tqdm progress bar by polling
    network interface stats or using a time-based estimate.
    Returns True on success, False on failure.
    """

    if not TQDM_AVAILABLE or total_bytes == 0:
        return _run_plain(cmd)

    result_holder = {"returncode": None, "error": ""}

    def run_proc():
        proc = subprocess.run(cmd, capture_output=True, text=True)
        result_holder["returncode"] = proc.returncode
        result_holder["error"] = proc.stderr.strip()

    thread = threading.Thread(target=run_proc, daemon=True)
    thread.start()

    # Poll /proc/net/dev to estimate bytes sent on all interfaces
    tx_start = _get_tx_bytes()
    transferred = 0

    bar_format = (
        "  [{bar:30}] {percentage:5.1f}%  "
        "{n_fmt}/{total_fmt}  {rate_fmt}  ETA {remaining}"
    )

    with tqdm(
        total=total_bytes,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
        desc=f"  {filename[:30]}",
        bar_format=bar_format,
        ncols=80,
        colour="cyan",
    ) as pbar:
        last_tx = tx_start
        while thread.is_alive():
            time.sleep(0.5)
            tx_now = _get_tx_bytes()
            delta = max(0, tx_now - last_tx)
            last_tx = tx_now
            increment = min(delta, total_bytes - transferred)
            if increment > 0:
                pbar.update(increment)
                transferred += increment

        # Fill to 100% on success
        thread.join()
        if result_holder["returncode"] == 0:
            remaining = total_bytes - transferred
            if remaining > 0:
                pbar.update(remaining)

    rc = result_holder["returncode"]
    if rc != 0:
        err = result_holder["error"]
        print(f"\n❌  SCP failed (exit {rc})")
        if err:
            _print_friendly_error(err)
        return False

    return True


def _run_plain(cmd):
    """Fallback: run scp without progress bar."""
    print("  Transferring... (install tqdm for progress bar)")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌  SCP failed: {result.stderr.strip()}")
        return False
    return True


def _get_tx_bytes():
    """Read total transmitted bytes from all network interfaces via /proc/net/dev."""
    total = 0
    try:
        with open("/proc/net/dev", "r") as f:
            lines = f.readlines()[2:]  # Skip header lines
        for line in lines:
            parts = line.split()
            if len(parts) >= 10:
                # TX bytes is the 10th column (index 9)
                try:
                    total += int(parts[9])
                except (ValueError, IndexError):
                    pass
    except Exception:
        pass
    return total


def _print_friendly_error(stderr):
    """Print a user-friendly error message based on scp/ssh stderr."""
    s = stderr.lower()
    if "connection refused" in s or "connection timed out" in s:
        print("    → Connection failed. Is the server online? Check host/port.")
    elif "authentication failed" in s or "permission denied" in s:
        print("    → Authentication failed. Check username/password.")
    elif "no such file or directory" in s:
        print("    → Remote destination path does not exist.")
    elif "network is unreachable" in s:
        print("    → Network unreachable. Check your connection.")
    else:
        print(f"    → {stderr[:200]}")
