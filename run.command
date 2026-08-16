#!/bin/bash
# GhostPrompter launcher for macOS.
# Double-click in Finder, or run ./run.command from a terminal.
#
# Unlike run.bat on Windows there is no bundled Python here, so this script
# bootstraps a local .venv on first run and reuses it afterwards.

set -euo pipefail

cd "$(dirname "$0")"

VENV=".venv"
PY="$VENV/bin/python"
STAMP="$VENV/.requirements-stamp"

find_python() {
    for candidate in python3.12 python3.11 python3; do
        if command -v "$candidate" >/dev/null 2>&1; then
            echo "$candidate"
            return 0
        fi
    done
    return 1
}

if [ ! -x "$PY" ]; then
    BOOTSTRAP_PY="$(find_python)" || {
        echo "Python 3 not found. Install it from https://www.python.org/downloads/ or run: brew install python"
        read -r -p "Press Enter to close..."
        exit 1
    }
    echo "Creating virtual environment with $BOOTSTRAP_PY..."
    "$BOOTSTRAP_PY" -m venv "$VENV"
fi

# Reinstall only when requirements.txt has actually changed, so normal startups
# stay fast.
REQ_HASH="$(shasum requirements.txt | awk '{print $1}')"
if [ ! -f "$STAMP" ] || [ "$(cat "$STAMP")" != "$REQ_HASH" ]; then
    echo "Installing dependencies..."
    "$PY" -m pip install --upgrade pip >/dev/null
    "$PY" -m pip install -r requirements.txt
    echo "$REQ_HASH" > "$STAMP"
fi

# The first run downloads the Vosk speech model (~50 MB per language), which
# takes a moment with no output of its own.
echo "Starting GhostPrompter..."
exec "$PY" main.py
