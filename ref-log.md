# Reference Log — external sources, tools, and GenAI usage

This file documents external libraries, tools, and GenAI usage for the assignment, plus a short rationale for each.

## Tools, libraries, and services used
- Streamlit — UI framework used to create a simple file upload and chat interface.
- LangChain (langchain, langchain-core, langchain-openai, langchain-community) — lightweight components for splitting text, document abstractions, and adapters to vector stores / models.
- ChromaDB — local vector store used to persist embeddings and perform similarity search.
- OpenAI-compatible proxy — institutional OpenAI-compatible proxy endpoint used to route chat and embedding calls (configured via `OPENAI_BASE_URL`).
- pypdf — used to extract text from PDF files when a user uploads a PDF; falls back gracefully if not present.
- Python 3.11 and pip — runtime and package manager.

## External references and documentation consulted
- Streamlit docs: https://docs.streamlit.io/
- LangChain docs and changelog: https://python.langchain.com/
- ChromaDB docs: https://www.trychroma.com/
- pypdf documentation: https://pypdf.readthedocs.io/
- OpenAI API spec (used as compatibility reference for the institutional proxy): https://platform.openai.com/docs/api-reference



## Reproducibility notes
- Minimal dependency list is provided in `requirements-min.txt` to help you install dependencies quickly.
- Full dependency snapshot (moved to `removed_for_simplify/constraints.txt`) was kept for reproducibility but is not required for the simplified app.

If you need more detail (exact package versions used during development, or the original exploratory notebooks), see the `removed_for_simplify/` folder which contains those artifacts.

---

## Use of an AI assistant (summary of what I asked the assistant to do)

I used an AI programming assistant while building this submission to accelerate iterative edits and to automate routine repo tasks. Below is a concise, transparent record of why I used the assistant and what it did for this project.

### Rationale for using the assistant
- Speed: accelerate repetitive edits (file edits, small scripts, and README updates) so I could focus on design and verification.
- Safety and reproducibility: automate structured, reversible repo edits (e.g., moving heavy artifacts to `removed_for_simplify/`, creating a simplified branch) so it's small and runnable.
- Guidance: produce a clear, minimal README and helper scripts that make the experience less error-prone.

### What the assistant did (actions I approved and reviewed)
- Inspected the repository and added a Streamlit UI enhancement to accept multiple files (.txt, .pdf) and extract text from PDFs with a pypdf fallback.
- Implemented a CLI smoke-test (`rag_app.py`) that ingests files from `./data/`, chunks text, creates embeddings, persists a Chroma index, and runs a retrieval+chat test.
- Added convenience artifacts: `run_streamlit.sh`, `.env.example`, and `requirements-min.txt` (minimal deps).
- Helped diagnose and resolve environment dependency issues (for example, guiding a numpy reinstall cycle); I performed the commands and validated imports.
- Managed the simplified submission workflow: created a `simplified` git branch, moved large or exploratory files into `removed_for_simplify/`, and produced a ZIP of the simplified workspace for download.
- Started and managed the Streamlit server in the Codespace for testing (I provided the API key in the session and confirmed the server saw the env vars).

### Privacy and safety note about the AI assistant
- No repository secrets (API keys) were committed. The assistant never logged or exfiltrated secret values; the API key was provided by me in the Codespace environment to run the app and tests.
- I reviewed and approved all code changes before committing them to the `simplified` branch.


