#!/usr/bin/env bash
set -euo pipefail

# Small helper to start Streamlit with required env checks.
# Usage: ./run_streamlit.sh

if [ -z "${OPENAI_API_KEY:-}" ] && [ -z "${API_KEY:-}" ]; then
  echo "ERROR: OPENAI_API_KEY or API_KEY must be set in this shell before running."
  echo "Example: export OPENAI_API_KEY=\"sk-...\""
  exit 1
fi

# Prefer OPENAI_API_KEY, else fallback to API_KEY
if [ -z "${OPENAI_API_KEY:-}" ]; then
  export OPENAI_API_KEY="${API_KEY}"
fi

: "${OPENAI_BASE_URL:?Please set OPENAI_BASE_URL, e.g. https://api.ai.it.cornell.edu}"

export OPENAI_CHAT_MODEL="${OPENAI_CHAT_MODEL:-openai.gpt-5-mini}"
export OPENAI_EMBEDDING_MODEL="${OPENAI_EMBEDDING_MODEL:-openai.text-embedding-3-small}"

echo "Starting Streamlit with the following settings:"
echo "  OPENAI_BASE_URL=${OPENAI_BASE_URL}"
echo "  OPENAI_CHAT_MODEL=${OPENAI_CHAT_MODEL}"
echo "  OPENAI_EMBEDDING_MODEL=${OPENAI_EMBEDDING_MODEL}"

streamlit run chat_with_pdf.py
