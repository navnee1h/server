# s2s — Send to Server

A CLI tool to transfer files and folders to a remote server. It uses SCP and SSH to handle uploads.

---

## Features

- **Progress Bar**: Shows upload progress in real-time.
- **Folder Compression**: Automatically zips folders larger than 50MB and extracts them on the server.
- **Notifications**: Sends a system alert when a transfer finishes or fails.
- **Tab Completion**: Supports auto-completion for paths, commands, and configuration keys.
- **History**: Keeps a log of transfers in `~/.s2s/history.log`.

---

## Installation

Run the installer script to set up dependencies and add `s2s` to your PATH:

```bash
chmod +x install.sh
./install.sh
source ~/.bashrc
```

*Note: Requires `openssh-client`, `sshpass`, and `python3`.*

---

## Configuration

Configure your server details before first use:

```bash
s2s edit host 192.168.1.10
s2s edit username yourname
s2s edit password yourpassword
s2s edit destination /home/yourname/Downloads
```

### Optional Settings

- `s2s edit port 22` (Default: 22)
- `s2s edit zip_threshold_mb 50` (Default: 50MB)

View your settings:

```bash
s2s show
```

---

## Usage

### Transfer Files or Folders

To send a file or a folder:

```bash
s2s /path/to/file_or_folder
```

### View History

Check your last 10 transfers:

```bash
s2s history
```

*Use `s2s history all` to see the full log.*

---

## Notes

- All configuration and logs are stored in `~/.s2s/`.
- Large folders are zipped to speed up the transfer.
- Tab completion works for files and commands.
