#!/usr/bin/env bash
# Zero45 – setup on Mac/Linux (once)
set -e
cd "$(dirname "$0")"
if ! command -v uv >/dev/null 2>&1; then
  echo "Installing uv ..."; curl -LsSf https://astral.sh/uv/0.11.32/install.sh | sh; export PATH="$HOME/.local/bin:$PATH"
fi
echo "Installing Python and packages (1-3 minutes) ..."
uv sync --frozen   # exactly the versions from uv.lock (with checksums)
uv run --frozen python -c "from ptz.game.runner import warmup; warmup(); print('OK')"
echo "Done. Start with:  bash start_spiel.sh   (single-player game: bash start_spiel.sh --solo)"
