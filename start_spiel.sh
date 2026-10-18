#!/usr/bin/env bash
# Zero45 – start the game (Mac/Linux). No option: network mode. --local: local mode with single-player game,
# --solo: local + open the single-player game. More options: --port 8000 --password X --host-remote --workers 3
cd "$(dirname "$0")"
export PATH="$HOME/.local/bin:$PATH"
exec uv run --frozen python -m ptz.server.app "$@"
