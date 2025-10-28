```markdown
# INFO 5940 — quick run guide
This repository contains a small Streamlit RAG demo and a CLI smoke-test (`rag_app.py`) that uses a Codespace-friendly OpenAI proxy.

Goal: make it trivial for an instructor or grader to run the assignment with the least terminal typing possible.

Requirements (what the runner must provide):
- A GitHub Codespace (or local machine) with Python 3.11 and pip installed.
- An API key for the institution proxy (do NOT commit your key).
- The proxy base URL used for OpenAI-compatible requests (for this repo we used `https://api.ai.it.cornell.edu`).

Quick steps — full copy/paste friendly

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

Files to look at
- `chat_with_pdf.py` — the Streamlit app UI (entrypoint used for the assignment)
- `rag_app.py` — a minimal end-to-end smoke-test: ingest -> chunk -> embed -> Chroma persist -> retrieve -> chat
- `langgraph_chroma_retreiver.ipynb` — exploratory notebook (optional)

Data folder and accepted file types
- Place all source files you want to ingest under the `./data/` directory.
- Supported file extensions: `.txt` and `.pdf`.
- The CLI smoke-test `rag_app.py` will load every supported file in `./data/`, create chunks, build/persist a Chroma index at `./chroma_db`, and then run a test retrieval + chat answer.

If you need to ingest other formats later (docx, html), I can add those with minimal changes.

Notes and gotchas
- Make sure your API key value is the raw token (sk-...), not prefixed with the literal string `Bearer `.
- Start Streamlit from the same shell/session that has the env vars exported; processes inherit env vars at launch.
- If your environment shows an error about a missing embedding model, set `OPENAI_EMBEDDING_MODEL` as shown above. The default fallback is `openai.text-embedding-3-small`.
- If you hit binary/compiled package import errors (e.g., `numpy.dtype size changed`), run a fresh `pip install --upgrade --force-reinstall numpy` and then reinstall compiled packages listed in `requirements.txt`.

Security
- Do not commit your API key. Use `.env` (not committed) or export it per-session.


Happy grading!

