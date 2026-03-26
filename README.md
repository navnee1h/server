# 🖥️ server — SCP File Transfer CLI Tool

A lightweight Python CLI tool that makes transferring files to your remote server fast, clean, and automated.

---

## 📁 Project Structure

```
server_tool/
├── server            ← Main executable (Python)
├── install.sh        ← One-shot installer
├── lib/
│   ├── cli.py        ← Command parser & router
│   ├── config.py     ← Config load/save/validate
│   ├── transfer.py   ← SCP transfer engine
│   ├── progress.py   ← tqdm progress bar
│   ├── history.py    ← Transfer history logger
│   ├── notifier.py   ← Desktop notifications
│   └── dependency.py ← Startup dependency checker
└── README.md
```

---

## 🚀 Installation

```bash
chmod +x install.sh
./install.sh
source ~/.bashrc
```

The installer will:
- Install system packages: `openssh-client`, `sshpass`, `zip`, `unzip`, `libnotify-bin`
- Install Python package: `tqdm`
- Copy the tool to `~/bin/server`
- Add `~/bin` to your `PATH`
- Set up bash tab completion

---

## ⚙️ Configuration

```bash
server edit host 192.168.1.10
server edit username yourname
server edit password yourpassword
server edit destination /home/yourname/Downloads
server edit port 22                  # optional, default: 22
server edit zip_threshold_mb 50      # optional, default: 50
```

View current config:
```bash
server show
```

Config is stored at: `~/.server_config.json`

---

## 📤 Usage

### Transfer a file
```bash
server /home/nav/file.txt
```

### Transfer a folder
```bash
server /home/nav/project/
```
> Folders larger than `zip_threshold_mb` are automatically zipped, uploaded, and extracted on the server.

### View transfer history
```bash
server history        # last 10
server history all    # everything
```

### Help
```bash
server help
```

---

## 📊 Progress Bar

```
  file.zip  [██████████████░░░░░░░░░] 65.2%  12.3M/18.9M  2.5MB/s  ETA 2s
```

---

## 📋 History Log

Stored at `~/.server_history.log`:

```
[2026-03-26 21:10] SUCCESS  file.txt → /home/server/Downloads
[2026-03-26 21:12] FAILED   project/ → /home/server/Downloads
```

---

## 🔔 Notifications

On transfer completion, a desktop notification is sent via `notify-send`:
- ✅ **Transfer Complete** — `file.txt uploaded successfully`
- ❌ **Transfer Failed** — `Check logs for details`

---

## 🔐 Dependencies

| Tool           | Purpose                        |
|----------------|--------------------------------|
| `scp`          | File transfer                  |
| `ssh`          | Remote command execution       |
| `sshpass`      | Password-based SSH automation  |
| `zip`/`unzip`  | Folder compression             |
| `notify-send`  | Desktop notifications          |
| `tqdm`         | Progress bar (Python)          |

---

## ⌨️ Tab Completion

After install, tab completion works automatically:

```bash
server /ho<TAB>          → /home/nav/
server edit <TAB>        → host username password destination port zip_threshold_mb
server history <TAB>     → all
```
