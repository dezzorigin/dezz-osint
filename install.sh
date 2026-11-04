#!/usr/bin/env bash
# dezz-osint one-liner installer (ala tools OSINT):
#   curl -sSL https://raw.githubusercontent.com/dezzorigin/dezz-osint/main/install.sh | bash
set -e
REPO="https://github.com/dezzorigin/dezz-osint.git"
DEST="${DEZZ_DIR:-$HOME/dezz-osint}"

echo "==> [1/4] clone $REPO -> $DEST"
if [ -d "$DEST/.git" ]; then
  git -C "$DEST" pull --ff-only
else
  git clone --depth 1 "$REPO" "$DEST"
fi
cd "$DEST"

echo "==> [2/4] venv"
[ -d .venv ] || python3 -m venv .venv

echo "==> [3/4] install (pip, may take a few minutes: maigret+selenium)"
.venv/bin/pip install --upgrade pip -q
.venv/bin/pip install . 

echo "==> [4/4] link binary -> ~/.local/bin/dezz"
mkdir -p ~/.local/bin
ln -sf "$DEST/.venv/bin/dezz" ~/.local/bin/dezz
ln -sf "$DEST/.venv/bin/dezzosint" ~/.local/bin/dezzosint
[ -f .env ] || cp .env.example .env

echo ""
echo "Done! Restart shell or: export PATH=\$HOME/.local/bin:\$PATH"
echo "  dezz phone +6281234567890"
echo "  dezz dossier example.com"
