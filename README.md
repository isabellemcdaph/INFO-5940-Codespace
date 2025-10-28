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

Notes and gotchas
- Make sure your API key value is the raw token (sk-...), not prefixed with the literal string `Bearer `.
- Start Streamlit from the same shell/session that has the env vars exported; processes inherit env vars at launch.
- If your environment shows an error about a missing embedding model, set `OPENAI_EMBEDDING_MODEL` as shown above. The default fallback is `openai.text-embedding-3-small`.
- If you hit binary/compiled package import errors (e.g., `numpy.dtype size changed`), run a fresh `pip install --upgrade --force-reinstall numpy` and then reinstall compiled packages listed in `requirements.txt`.

Security
- Do not commit your API key. Use `.env` (not committed) or export it per-session.

If you want, I can also create a single-file runnable script that installs deps and runs the app (I did not add that to avoid re-installing packages automatically inside grader environments).

Happy grading — if you'd like I can also:
- produce a minimal `requirements-min.txt` with only the packages required to run the Streamlit app and `rag_app.py`, or
- create a one-click GitHub Actions workflow that runs the smoke test (useful for CI).

```
# INFO 5940 
Welcome to the INFO 5940 repository. You will complete your work using [**GitHub Codespaces**](#about-github-codespaces) and save your progress in your own GitHub repository. This guide will walk you through setting up the development environment and running the test notebook.  

## Getting Started 

### Step 1: Fork this repository 
1. Click the **Fork** button (top right of this page).
2. This will create a copy of the repo under **your own GitHub account**.

Forking creates a personal copy of the repo under **your** GitHub account.  
- You can commit, push, and experiment freely.  
- Your work stays separate from the official class materials.

### Step 2: Open your forked repo Codespace
1. Go to **your forked repo**.
2. Click the green **Code** button and switch to the **Codespaces** tab.  
3. Select **Create Codespace**.
4. Wait a few minutes for the environment to finish setting up.

### Step 3: Verify your environment 
Once the Codespace is ready: 
1. If you are in `<your-file-name>.ipynb` in your codespace.
2. Install the Python 3.11.13 Kernel.  In the top-right corner, click **Select Kernel**.
    1. If **Install/Enable suggested extensions Python + Jupyter** appears, select it, and wait for the install to finish before moving on to the next step.
    2. Select **Python Environments** choose **Python 3.11.13 (first option)**.
3. Run the code block to check your setup. 

## About GitHub Codespaces

[Codespaces](https://docs.github.com/en/codespaces) is a complete software development and execution environment, running in the cloud, with its primary interface being a VSCode instance running in your browser.

Codespaces is not free, but their per-month [free quota](https://docs.github.com/en/billing/concepts/product-billing/github-codespaces#free-quota) is generous.  Codespaces is free under the [GitHub Student Developer Pack](https://education.github.com/pack#github-codespaces).

### Codespaces Tips

* Codespaces keep running even when you close your browser (but will time out and stop after a while)
* Unless you're on a free plan, or within your free quota, costs acrue while the codespace is running, whether or not you have it open in your browser or are working on it
* You can control when it's running, and the space it takes up.  Check out [GitHub's codespaces lifecycle documentation](https://docs.github.com/en/codespaces/about-codespaces/understanding-the-codespace-lifecycle)

## Sync Updates 
To make sure your personal forked repository stays up to date with the original class repository, please follow these steps:
1. Open your forked repo.
2. At the top of the page, you should see a banner or menu option that shows whether your fork is behind the original repo.
3. Click the **Sync fork** button.
4. In the dropdown, choose **Update branch** to pull the latest changes from the original repo into your fork.

Optionally, you can also follow these steps to create a new branch on your fork:
1. Open your **forked repository** on GitHub.  
2. At the top of the page, next to the branch dropdown, click the **Branches** button.  
3. In the **Branches** view, click the green **New Branch** button.  
4. In the popup window, enter a branch name.  
   - You can use any name you like, but it’s recommended to match the branch name used in class for better organization.  
5. Under **Branch source**, select:  
   - **Repository:** `AyhamB/INFO-5940-Codespace`  
   - **Branch:** choose the branch you want to sync from (e.g., `streamlit`).  
6. Click the green **Create New Branch** button.  
7. Verify that you’re now back in **your fork**, on the new branch you just created.  
8. Click the **Code** button and create a new Codespace (if you don’t already have one).  
   - Make sure the Codespace is created from the **current branch**.
  
## Running a Streamlit App on Codespaces  
Follow these steps to launch and view your Streamlit app in GitHub Codespaces:
1. **Open the terminal** inside your Codespace.
2. Run the command:  
   ```bash
   streamlit run your-file-name.py
   ```  
   **(Replace `your-file-name.py` with the actual name of your Streamlit app file, e.g., `hello_app.py`.)**
3. After pressing **Enter**, a popup should appear in the bottom-right corner of Codespace editor.  
   - Click **“Open in Browser”** to view your app.  

   ⚠️ *If you miss the popup:*  
   - Press **Ctrl + C** in the terminal to stop the app.  
   - Rerun the command from step 2 — the popup should appear again.
4. A new browser tab will open, showing the interface of your Streamlit app.
5. **Make changes to your code** in the Codespace editor.  
   - Refresh the browser tab to see the updated version of your app.  

## Setting Your API Key in GH Codespaces
You will receive an individual API Key for class assignments. To prevent accidental exposure online, please follow the steps below to securely insert your key in the terminal.
1. **Open the terminal** inside your Codespace.
2. Run the command to temporarily set your API Key for this session:  
   ```bash
   export API_KEY="your_actual_API_KEY"
   ```
3. If you want to run the Streamlit app and set up the key at the same time, run both commands together:
   ```bash
   API_KEY="your_actual_API_KEY" streamlit run your-file-name.py
   ```

## Troubleshooting
- The Jupyter extension should install automatically. If you still cannot select a Python kernel on Jupyter Notebook: Go to the left sidebar >> **Extensions** >> search for **Jupyter** >> reload window (or reinstall it).   
