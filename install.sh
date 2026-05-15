#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
#  server CLI Tool - Installer
#  Installs the tool to ~/bin and sets up bash tab completion
# ─────────────────────────────────────────────────────────────

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$HOME/bin"
TOOL_DEST="$BIN_DIR/s2s"
LIB_DEST="$BIN_DIR/s2s_lib"
COMPLETION_FILE="$HOME/.bash_completion.d/s2s"
BASHRC="$HOME/.bashrc"

echo ""
echo "╔══════════════════════════════════════╗"
echo "║      s2s CLI Tool - Installer        ║"
echo "╚══════════════════════════════════════╝"
echo ""

# ── 1. Create ~/bin if needed ──────────────────────────────────
mkdir -p "$BIN_DIR"
mkdir -p "$HOME/.bash_completion.d"
mkdir -p "$HOME/.s2s"

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
cp "$SCRIPT_DIR/s2s" "$TOOL_DEST"
chmod +x "$TOOL_DEST"

rm -rf "$LIB_DEST"
cp -r "$SCRIPT_DIR/lib" "$LIB_DEST"

# Patch the LIB_DIR path in the main script to point to new location
sed -i "s|LIB_DIR = os.path.join(SCRIPT_DIR, \"lib\")|LIB_DIR = os.path.expanduser(\"~/bin/s2s_lib\")|g" "$TOOL_DEST"

echo "✅  Files installed to $BIN_DIR"
echo ""

# ── 5. Add ~/bin to PATH if not already there ─────────────────
if ! grep -q 'export PATH="$HOME/bin:$PATH"' "$BASHRC" 2>/dev/null; then
    echo "" >> "$BASHRC"
    echo '# Added by s2s CLI installer' >> "$BASHRC"
    echo 'export PATH="$HOME/bin:$PATH"' >> "$BASHRC"
    echo "✅  Added ~/bin to PATH in ~/.bashrc"
fi

# ── 6. Install bash tab completion ────────────────────────────
cat > "$COMPLETION_FILE" << 'EOF'
# Tab completion for s2s CLI tool
_s2s_completion() {
    local cur prev words cword
    _init_completion || return

    local commands="show edit history help"
    local edit_keys="host username password destination port zip_threshold_mb"

    case "$prev" in
        s2s)
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

complete -F _s2s_completion s2s
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
echo "║  Then configure your s2s:                        ║"
echo "║    s2s edit host 192.168.1.10                    ║"
echo "║    s2s edit username yourname                    ║"
echo "║    s2s edit password yourpassword                ║"
echo "║    s2s edit destination /home/you/Downloads      ║"
echo "║                                                  ║"
echo "║  Start transferring:                             ║"
echo "║    s2s /path/to/file.txt                         ║"
echo "║    s2s /path/to/folder/                          ║"
echo "║                                                  ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""
