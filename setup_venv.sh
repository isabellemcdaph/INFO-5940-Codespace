#!/usr/bin/env bash
set -euo pipefail

# Helper to create a virtualenv, upgrade pip and related tooling, and install requirements.
# Usage: ./setup_venv.sh

VENV_DIR=".venv-grader"
REQ_FILE="requirements-min.txt"

if [ -d "$VENV_DIR" ]; then
  echo "Using existing virtualenv at $VENV_DIR"
else
  echo "Creating virtualenv at $VENV_DIR"
  python3 -m venv "$VENV_DIR"
fi

echo "Upgrading pip, setuptools, wheel in the virtualenv..."
"$VENV_DIR/bin/python" -m pip install --upgrade pip setuptools wheel

if [ -f "$REQ_FILE" ]; then
  echo "Installing requirements from $REQ_FILE"
  "$VENV_DIR/bin/python" -m pip install -r "$REQ_FILE"
else
  echo "Requirements file $REQ_FILE not found. Aborting." >&2
  exit 1
fi

echo
echo "Done. Activate the virtualenv with:"
echo "  source $VENV_DIR/bin/activate"
echo "Then run the app with:"
echo "  python -m streamlit run chat_with_pdf.py"
