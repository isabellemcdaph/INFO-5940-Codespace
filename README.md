# Background

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

1) Install python deps (run once in the Codespace terminal, it may ask you to upgrade pip if you haven't recently):

Note: I recommend creating and activating a virtual environment before installing to ensure tools like `streamlit` are placed on the active PATH and to avoid user-site installs. Example:

```bash
python3 -m venv .venv-grader
source .venv-grader/bin/activate
```

Then install dependencies:

```bash
python3 -m pip install -r requirements-min.txt
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

## Set the notebook kernel (Codespaces / VS Code)

1. Open the notebook file in VS Code — e.g. `langgraph_chroma_retreiver.merged.ipynb` 
2. In the top-right of the notebook editor, click `Select Kernel`.
	- If VS Code suggests "Install/Enable extensions Python + Jupyter", accept and wait for the install to finish.
3. Choose `Python Environments` and select the interpreter matching the project (pick the Python 3.11.13 environment if available, or the project's virtualenv such as `.venv-grader/bin/python`).
	- If you followed the README and created a virtualenv (example `.venv-grader`), ensure that virtualenv's interpreter appears in the list and select it.
4. After switching kernels, run a small cell to confirm imports work, for example:

```python
import sys
print(sys.executable)
```

Notes:
- If you prefer reproducible environments, use the repo devcontainer (open in Codespaces) which will pick the correct Python automatically.
- If the kernel is missing from the list, activate the virtualenv in a terminal inside VS Code and re-open the notebook or restart VS Code so the interpreter is discovered.



# What changed from the assignment template:

In short:
Large or exploratory artifacts (original notebooks, a persisted Chroma DB, and the full dependency snapshot) were moved into `removed_for_simplify/` so you see a compact, runnable project. I also added a minimal dependency file (`requirements-min.txt`), a small startup helper (`run_streamlit.sh`), and a CLI smoke-test (`rag_app.py`). Functionally, `chat_with_pdf.py` was updated to accept multiple files (.txt/.pdf), extract text from PDFs, optionally build a small Chroma index, and run a context-grounded chat query.

- I added a minimal dependency file `requirements-min.txt` for simplicity's sake. It only includes a minimal set of packages needed to run the Streamlit app and CLI smoke test. If you need the full constraints snapshot for reproducibility, it's in `removed_for_simplify/constraints.txt`.

Here are the packages present in my updated requirements-min.txt but not in original requirements.txt

chromadb>=1.2
langchain-text-splitters
langchain-core==0.3.79 (note: original uses package name with an underscore: langchain_core==0.3.79 — see below)
(I also list pandas with no pinned version in the minimal file; upstream pins pandas==2.)

Here are the packages present in requirements.txt but omitted from requirements-min.txt 

aioboto3==12
fsspec
pydantic # 2.12.0
s3fs
cfn_flip
cfn-lint
ipykernel
notebook
openpyxl
beautifulsoup4
pyarrow
litellm # 1.77.7
protobuf>=4.21.6,<5.0.0
(and a few others used for heavier dev/notebook workflows)

- `.devcontainer/` was not modified — the original devcontainer configuration is intact and present in the repository. Use the provided devcontainer to reproduce the original development environment if required.

- Other helper files added: `run_streamlit.sh` (checks env and runs the app), `.env.example` (example env vars), and `rag_app.py` (CLI smoke-test).

- I also made specifications for which models (gpt-5 mini, etc) to use.

Overall file changes:

Files added to the simplified branch (or modified):

.env.example — small env-template example added.
README.md — updated 
chat_with_pdf.py — edited (UI now supports multi-file uploads + PDF extraction & optional RAG flow).
langgraph_chroma_retreiver.merged.ipynb — added merged/sanitized notebook.
rag_app.py — new CLI smoke-test (ingest → chunk → embed → Chroma → retrieve → chat).
requirements-min.txt — new minimal requirements
run_streamlit.sh — small run wrapper that checks env vars and starts Streamlit.
removed_for_simplify/* — several large/heavy items were moved into this folder (persisted Chroma DB, original notebooks, full requirements.txt, constraints.txt, compiled caches, etc.) so the root repo is small

Files relocated to removed_for_simplify (kept as backup, not deleted):

requirements.txt (full), constraints.txt, original notebooks (langgraph_chroma_retreiver.ipynb, edited notebook), a persisted chroma_db/, and other heavy items.

