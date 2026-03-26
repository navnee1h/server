# SCP File Transfer CLI Tool

A lightweight Python-based command-line interface (CLI) designed to simplify and automate file transfers to a remote server. This tool wraps SCP and SSH functionality to provide features like folder auto-zipping, progress bars, and transfer history.

## Personal Project Note
This is a personal project I built to speed up the workflow of sending files between my laptop and my local server. 

**Please Note:** Security was not the primary focus during development as this tool is intended for use within a trusted local network. If you plan to use this in a personal capacity, feel free to fork the repository and update it to your needs—especially if you require SSH key-based authentication.

---

## Project Structure

```bash
server_tool/
├── server            # Main executable (Python)
├── install.sh        # One-shot installer script
├── lib/
│   ├── cli.py        # Command parser and routing logic
│   ├── config.py     # Configuration management (load/save/validate)
│   ├── transfer.py   # SCP transfer engine
│   ├── progress.py   # tqdm progress bar integration
│   ├── history.py    # Transfer history logging
│   ├── notifier.py   # Desktop notifications (libnotify)
│   └── dependency.py # Startup dependency verification
└── README.md
````

---

## Installation

To set up the tool on your system, run the following commands:

```bash
chmod +x install.sh
./install.sh
source ~/.bashrc
```

**The installer performs the following actions:**

- Installs necessary system packages: `openssh-client`, `sshpass`, `zip`, `unzip`, and `libnotify-bin`.
- Installs the `tqdm` Python library for progress tracking.
- Copies the tool to `~/bin/server`.
- Adds `~/bin` to your system `PATH`.
- Configures Bash tab completion for easier usage.

---

## Configuration

Before the first use, configure your server details:

```bash
server edit host 192.168.1.10
server edit username yourname
server edit password yourpassword
server edit destination /home/yourname/Downloads

# Optional settings
server edit port 22                  # Default is 22
server edit zip_threshold_mb 50      # Threshold for auto-zipping folders (Default: 50MB)
```

To view your current settings:

```bash
server show
```

_Note: Settings are stored locally in `~/.server_config.json`._

---
## Usage

### Transferring Files

To send a single file:

```bash
server /path/to/file.txt
```

### Transferring Folders

To send an entire directory:

```bash
server /path/to/folder/
```

_If a folder exceeds the `zip_threshold_mb` setting, the tool automatically zips the folder, uploads it, and extracts it on the destination server._

### Transfer History

Check your recent activity:

```bash
server history        # Displays the last 10 transfers
server history all    # Displays the full log
```

### Help

For a full list of commands:

```bash
server help
```

---

## Features

- **Progress Tracking:** A real-time progress bar shows upload percentage, transfer speed, and estimated time remaining.
- **Desktop Notifications:** Uses `notify-send` to alert you when a transfer completes or fails.
- **Logging:** All activity is recorded in `~/.server_history.log`.
- **Tab Completion:** Supports auto-completion for file paths and configuration keys.

---

## Dependencies

The tool relies on the following utilities.

|**Tool**|**Purpose**|
|---|---|
|**scp**|Core file transfer|
|**ssh**|Remote command execution|
|**sshpass**|Automated password authentication|
|**zip/unzip**|Folder compression and extraction|
|**notify-send**|Desktop alerts|
|**tqdm**|Python-based progress bar|

---
## License & Contributions

This project is open-source. Since this was built for a specific local use case, you are encouraged to fork the repository and update it to fit your own requirements, especially regarding SSH key authentication or enhanced security protocols.
