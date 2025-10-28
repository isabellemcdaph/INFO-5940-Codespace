"""
Simple RAG smoke-test script.

Behavior summary:
- Loads `./data/RAG_source.txt` (expects a plain .txt file)
- Splits with chunk_size=1000, chunk_overlap=0 (defaults; overridable via env)
- Embeds with OpenAI-compatible embeddings (model from env `OPENAI_EMBEDDING_MODEL`)
- Indexes into a local Chroma DB at `./chroma_db` (persist dir overridable via env)
- Retrieves top-k (default k=4) and calls a chat model (env `OPENAI_CHAT_MODEL`) to produce an answer

Environment notes (used by this script):
- `OPENAI_API_KEY` (or fallback `API_KEY`) — must hold the raw token (sk-...), NOT the literal prefix `Bearer `
- `OPENAI_BASE_URL` / `OPENAI_API_BASE` — set to your proxy base URL (e.g. `https://api.ai.it.cornell.edu`)
- `OPENAI_EMBEDDING_MODEL`, `OPENAI_CHAT_MODEL` — optional overrides; defaults are reasonable for grading

Run: python3 rag_app.py
"""
import os
import sys
from pathlib import Path

print('Starting RAG smoke test...')

DATA_DIR = Path('./data')
if not DATA_DIR.exists() or not any(DATA_DIR.iterdir()):
    print('Error: expected one or more source files in ./data (supported: .txt, .pdf)')
    sys.exit(1)

# sensible defaults and env overrides
CHUNK_SIZE = int(os.environ.get('RAG_CHUNK_SIZE', 1000))
CHUNK_OVERLAP = int(os.environ.get('RAG_CHUNK_OVERLAP', 0))
K = int(os.environ.get('RAG_RETRIEVER_K', 4))
PERSIST_DIR = os.environ.get('RAG_PERSIST_DIR', './chroma_db')
EMBEDDING_MODEL = os.environ.get('OPENAI_EMBEDDING_MODEL', 'openai.text-embedding-3-small')
CHAT_MODEL = os.environ.get('OPENAI_CHAT_MODEL', 'openai.gpt-5-mini')

# Ensure OPENAI_API_KEY is present (fall back to API_KEY if provided by Codespace template)
if not os.environ.get('OPENAI_API_KEY') and os.environ.get('API_KEY'):
    os.environ['OPENAI_API_KEY'] = os.environ['API_KEY']
    print('Using API_KEY as OPENAI_API_KEY fallback')

# Optionally set OPENAI_API_BASE/OPENAI_BASE_URL compatibility
if not os.environ.get('OPENAI_API_BASE') and os.environ.get('OPENAI_BASE_URL'):
    os.environ['OPENAI_API_BASE'] = os.environ['OPENAI_BASE_URL']
print(f'Config: chunk_size={CHUNK_SIZE}, chunk_overlap={CHUNK_OVERLAP}, k={K}')
print(f'Embedding model: {EMBEDDING_MODEL}, Chat model: {CHAT_MODEL}')

# imports (do at runtime to show helpful errors)
try:
    from langchain_community.document_loaders import TextLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain.embeddings import OpenAIEmbeddings
    from langchain.vectorstores import Chroma
    from langchain.chat_models import ChatOpenAI
    from langchain.schema import HumanMessage, SystemMessage
except Exception as e:
    print('Import error: ', e)
    print('Make sure required packages are installed (see requirements.txt).')
    raise

# load all supported files from ./data (txt and pdf). We try to use langchain loaders when
# available and fall back to lightweight readers if not.
docs = []

# Document class fallback (try langchain_core, then langchain.schema, else simple container)
try:
    from langchain_core.documents import Document
except Exception:
    try:
        from langchain.schema import Document
    except Exception:
        class Document:
            def __init__(self, page_content, metadata=None):
                self.page_content = page_content
                self.metadata = metadata or {}

for path in sorted(DATA_DIR.iterdir()):
    if path.suffix.lower() == '.txt':
        try:
            loader = TextLoader(str(path))
            file_docs = loader.load()
        except Exception:
            # fallback: simple read
            text = path.read_text(encoding='utf-8', errors='ignore')
            file_docs = [Document(page_content=text, metadata={'source': str(path)})]
    elif path.suffix.lower() == '.pdf':
        # prefer langchain's PyPDFLoader if available
        try:
            from langchain.document_loaders import PyPDFLoader
            loader = PyPDFLoader(str(path))
            file_docs = loader.load()
        except Exception:
            # fallback to pypdf extraction
            try:
                from pypdf import PdfReader
                reader = PdfReader(str(path))
                text = '\n\n'.join((page.extract_text() or '') for page in reader.pages)
                file_docs = [Document(page_content=text, metadata={'source': str(path)})]
            except Exception as e:
                print(f'Warning: failed to load PDF {path}: {e}')
                file_docs = []
    else:
        # skip unsupported types
        print(f'Skipping unsupported file type: {path.name}')
        file_docs = []

    docs.extend(file_docs)

if not docs:
    print('No documents were loaded from ./data — aborting.')
    sys.exit(1)

print(f'Loaded {len(docs)} source documents (showing first source):')
first = docs[0]
print(first.page_content[:200].replace('\n',' ') + ('...' if len(first.page_content) > 200 else ''))

# split
splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
chunks = splitter.split_documents(docs)
print(f'Created {len(chunks)} chunks')

# embeddings and vectorstore
print('Creating embeddings and Chroma index (this may take a moment)')
emb = OpenAIEmbeddings(model=EMBEDDING_MODEL)
try:
    vectordb = Chroma.from_documents(documents=chunks, embedding=emb, persist_directory=PERSIST_DIR)
    print('Chroma index created/persisted at', PERSIST_DIR)
except Exception as e:
    print('Error creating Chroma vectorstore:', type(e).__name__, e)
    raise

# retrieval
print(f'Retrieving top {K} chunks for a test query')
query = os.environ.get('RAG_TEST_QUERY', 'What is Zelomax?')
try:
    # use similarity_search if available
    docs_found = vectordb.similarity_search(query, k=K)
except Exception:
    # fallback to retriever
    retriever = vectordb.as_retriever(search_type='similarity', search_kwargs={'k': K})
    docs_found = retriever.get_relevant_documents(query)

print(f'Retrieved {len(docs_found)} docs — printing snippets:')
for i,d in enumerate(docs_found, start=1):
    snippet = d.page_content[:400].replace('\n',' ')
    src = d.metadata.get('source', '(no source)') if hasattr(d, 'metadata') else '(no metadata)'
    snippet_preview = snippet[:200] + ('...' if len(snippet) > 200 else '')
    print(f"[{i}] source={src} snippet=\"{snippet_preview}\"")

# attempt to call chat model with context
print('\nAttempting to call chat model to answer using retrieved context...')
system_instructions = (
    'You are a concise question-answering assistant. Use ONLY the provided context to answer the question. Keep answers <= 3 sentences. If unknown, say you do not know.'
)
context_text = '\n\n---\n\n'.join(d.page_content for d in docs_found)
prompt = f"Context:\n{context_text}\n\nQuestion: {query}\n\nAnswer:" 

try:
    llm = ChatOpenAI(model=CHAT_MODEL, temperature=0)
    messages = [SystemMessage(content=system_instructions), HumanMessage(content=prompt)]
    resp = llm(messages)
    # llm(messages) may return a ChatResult or BaseMessage depending on version
    if hasattr(resp, 'content'):
        out = resp.content
    else:
        # try to extract from structure
        try:
            out = resp.generations[0][0].text
        except Exception:
            out = str(resp)
    print('\nModel answer:')
    print(out)
except Exception as e:
    print('Chat model call failed:', type(e).__name__, e)
    print('But ingestion/retrieval completed — RAG index is usable.')

print('\nDone')
