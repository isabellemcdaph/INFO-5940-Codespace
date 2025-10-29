```markdown
# Background
This repository contains a small Streamlit RAG demo and a CLI smoke-test (`rag_app.py`) that uses a Codespace-friendly OpenAI proxy.

Once run in browser, you can upload documents in either .txt or .pdf and ask the chatbot to answer questions about your files.

Overview — what this project does

- Streamlit UI (`chat_with_pdf.py`): upload one or more text/PDF files and ask questions. The app extracts text, optionally builds a small Chroma vector index, retrieves top-k context, and calls a chat model to answer.
- CLI smoke-test (`rag_app.py`): run a minimal ingest → chunk → embed → Chroma persist → retrieve → chat flow from the terminal for quick grading.
- Data-driven: place `.txt` or `.pdf` files into `./data/` for CLI ingestion.

Requirements (what the runner must provide):
- A GitHub Codespace (or local machine) with Python 3.11 and pip installed.
- An API key for the institution proxy (do NOT commit your key).
- The proxy base URL used for OpenAI-compatible requests (for this repo we used `https://api.ai.it.cornell.edu`).


# Quick steps 

1) Install python deps (run once in the Codespace terminal):

```bash
python3 -m pip install -r requirements.txt
```

2) Create a small env file (recommended) or export env vars in the terminal. Example (preferred — copy/paste and replace the token):

```bash
# Option A) temporary env in the shell (recommended for security)
export OPENAI_API_KEY="sk-..."                      # your token (raw sk-... value, NOT 'Bearer sk-...')
export OPENAI_BASE_URL="https://api.ai.it.cornell.edu"  # your proxy base URL
export OPENAI_CHAT_MODEL="openai.gpt-5-mini"         # chat model (optional override)
export OPENAI_EMBEDDING_MODEL="openai.text-embedding-3-small"  # embedding model (optional override)

# Option B) load from .env file (we include .env.example)
# cp .env.example .env && source .env
```

3) Start the Streamlit app (one command — starts in foreground so you can see logs):

```bash
# from the repo root
./run_streamlit.sh
```

What `run_streamlit.sh` does: ensures required env vars are present (safe checks), then runs `streamlit run chat_with_pdf.py` with your env preserved.

Quick smoke-test (CLI) — use this to validate the proxy and embedding/chat endpoints without the UI:

```bash
python3 rag_app.py            # creates ./chroma_db/, runs a small retrieval and prints a model answer
```


# What changed from the assignment template:

In short:
Large or exploratory artifacts (original notebooks, a persisted Chroma DB, and the full dependency snapshot) were moved into `removed_for_simplify/` so you see a compact, runnable project. I also added a minimal dependency file (`requirements-min.txt`), a small startup helper (`run_streamlit.sh`), and a CLI smoke-test (`rag_app.py`). Functionally, `chat_with_pdf.py` was updated to accept multiple files (.txt/.pdf), extract text from PDFs, optionally build a small Chroma index, and run a context-grounded chat query.

Specifically:
Files added to the simplified branch (or modified):

.env.example — small env-template example added.
README.md — updated for the simplified/grader view.
chat_with_pdf.py — edited (UI now supports multi-file uploads + PDF extraction & optional RAG flow).
langgraph_chroma_retreiver.merged.ipynb — added merged/sanitized notebook.
rag_app.py — new CLI smoke-test (ingest → chunk → embed → Chroma → retrieve → chat).
requirements-min.txt — new minimal requirements for graders.
run_streamlit.sh — small run wrapper that checks env vars and starts Streamlit.
removed_for_simplify/* — several large/heavy items were moved into this folder (persisted Chroma DB, original notebooks, full requirements.txt, constraints.txt, compiled caches, etc.) so the root repo is small and grade-friendly.
Files relocated to removed_for_simplify (kept as backup, not deleted):

requirements.txt (full), constraints.txt, original notebooks (langgraph_chroma_retreiver.ipynb, edited notebook), a persisted chroma_db/, and other heavy items.

