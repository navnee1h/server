#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
#  server CLI Tool - Installer
#  Installs the tool to ~/bin and sets up bash tab completion
# ─────────────────────────────────────────────────────────────

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$HOME/bin"
TOOL_DEST="$BIN_DIR/server"
LIB_DEST="$BIN_DIR/server_lib"
COMPLETION_FILE="$HOME/.bash_completion.d/server"
BASHRC="$HOME/.bashrc"

echo ""
echo "╔══════════════════════════════════════╗"
echo "║    Server CLI Tool - Installer       ║"
echo "╚══════════════════════════════════════╝"
echo ""

# ── 1. Create ~/bin if needed ──────────────────────────────────
mkdir -p "$BIN_DIR"
mkdir -p "$HOME/.bash_completion.d"

# ── 2. Install system dependencies ────────────────────────────
echo "📦  Installing system dependencies..."
sudo apt-get update -qq
sudo apt-get install -y -qq openssh-client sshpass zip unzip libnotify-bin
echo "✅  System dependencies installed."
echo ""

# ── 3. Install Python dependency (tqdm) ───────────────────────
echo "🐍  Installing Python dependencies..."
pip install --quiet tqdm 2>/dev/null || pip3 install --quiet tqdm 2>/dev/null || {
    echo "⚠️   Could not install tqdm. Progress bar will be basic."
}
echo "✅  Python dependencies ready."
echo ""

# ── 4. Copy files to ~/bin ────────────────────────────────────
echo "📂  Copying files to $BIN_DIR..."
cp "$SCRIPT_DIR/server" "$TOOL_DEST"
chmod +x "$TOOL_DEST"

rm -rf "$LIB_DEST"
cp -r "$SCRIPT_DIR/lib" "$LIB_DEST"

# Patch the LIB_DIR path in the main script to point to new location
sed -i "s|LIB_DIR = os.path.join(SCRIPT_DIR, \"lib\")|LIB_DIR = os.path.expanduser(\"~/bin/server_lib\")|g" "$TOOL_DEST"

echo "✅  Files installed to $BIN_DIR"
echo ""

# ── 5. Add ~/bin to PATH if not already there ─────────────────
if ! grep -q 'export PATH="$HOME/bin:$PATH"' "$BASHRC" 2>/dev/null; then
    echo "" >> "$BASHRC"
    echo '# Added by server CLI installer' >> "$BASHRC"
    echo 'export PATH="$HOME/bin:$PATH"' >> "$BASHRC"
    echo "✅  Added ~/bin to PATH in ~/.bashrc"
fi

# ── 6. Install bash tab completion ────────────────────────────
cat > "$COMPLETION_FILE" << 'EOF'
# Tab completion for server CLI tool
_server_completion() {
    local cur prev words cword
    _init_completion || return

    local commands="show edit history help"
    local edit_keys="host username password destination port zip_threshold_mb"

    case "$prev" in
        server)
            # Complete with commands or paths
            local IFS=$'\n'
            local path_completions
            mapfile -t path_completions < <(compgen -f -- "$cur")
            COMPREPLY=( $(compgen -W "$commands" -- "$cur") "${path_completions[@]}" )
            ;;
        edit)
            COMPREPLY=( $(compgen -W "$edit_keys" -- "$cur") )
            ;;
        history)
            COMPREPLY=( $(compgen -W "all" -- "$cur") )
            ;;
        *)
            # Default to file/dir completion
            COMPREPLY=( $(compgen -f -- "$cur") )
            ;;
    esac
}

complete -F _server_completion server
EOF

# Source bash completions in .bashrc if not already done
if ! grep -q 'bash_completion.d' "$BASHRC" 2>/dev/null; then
    echo "" >> "$BASHRC"
    echo '# Load bash completions' >> "$BASHRC"
    echo 'for f in ~/.bash_completion.d/*; do source "$f" 2>/dev/null; done' >> "$BASHRC"
    echo "✅  Bash completion installed."
fi

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║  ✅  Installation complete!                      ║"
echo "╠══════════════════════════════════════════════════╣"
echo "║                                                  ║"
echo "║  Reload your shell:                              ║"
echo "║    source ~/.bashrc                              ║"
echo "║                                                  ║"
echo "║  Then configure your server:                     ║"
echo "║    server edit host 192.168.1.10                 ║"
echo "║    server edit username yourname                 ║"
echo "║    server edit password yourpassword             ║"
echo "║    server edit destination /home/you/Downloads   ║"
echo "║                                                  ║"
echo "║  Start transferring:                             ║"
echo "║    server /path/to/file.txt                      ║"
echo "║    server /path/to/folder/                       ║"
echo "║                                                  ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""
