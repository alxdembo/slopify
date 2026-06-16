#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SLOPIFY="python $SCRIPT_DIR/slopify.py"

echo "==> Installing dependencies..."
pkg install python ffmpeg -y
pip install yt-dlp

echo "==> Setting up shared storage..."
termux-setup-storage || true

# Pick shell rc
if [ -f "$HOME/.zshrc" ]; then
    SHELL_RC="$HOME/.zshrc"
else
    SHELL_RC="$HOME/.bashrc"
fi

# Remove previous slopify block if present
sed -i '/# slopify-start/,/# slopify-end/d' "$SHELL_RC"

cat >> "$SHELL_RC" << EOF

# slopify-start
s() { $SLOPIFY s "\$@"; }
a() { $SLOPIFY a "\$@"; }
r() { $SLOPIFY r "\$@"; }
_slopify_banner() {
    local stamp="\$HOME/.slopify_banner_date"
    local today=\$(date +%Y-%m-%d)
    if [ ! -f "\$stamp" ] || [ "\$(cat \$stamp)" != "\$today" ]; then
        cat << 'BANNER'
           ░██                       ░██    ░████
           ░██                             ░██
 ░███████  ░██  ░███████  ░████████  ░██░████████ ░██    ░██
░██        ░██ ░██    ░██ ░██    ░██ ░██   ░██    ░██    ░██
 ░███████  ░██ ░██    ░██ ░██    ░██ ░██   ░██    ░██    ░██
       ░██ ░██ ░██    ░██ ░███   ░██ ░██   ░██    ░██   ░███
 ░███████  ░██  ░███████  ░██░█████  ░██   ░██     ░█████░██
                          ░██                            ░██
                          ░██                      ░███████
BANNER
        echo "\$today" > "\$stamp"
    fi
}
_slopify_banner
# slopify-end
EOF

echo ""
echo "Done. Restart your shell or run:  source $SHELL_RC"
echo ""
echo "Usage:"
echo "  s master of puppets"
echo "  a chocolate starfish"
echo "  r prodigy breathe"
