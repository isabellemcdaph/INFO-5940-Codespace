"""
Simple RAG smoke-test script.
- Loads ./data/RAG_source.txt (expects .txt)
- Splits with chunk_size=1000, chunk_overlap=0
- Embeds with OpenAI embeddings model (env OPENAI_EMBEDDING_MODEL)
- Indexes into Chroma at ./chroma_db
- Retrieves top-k (k=4) and attempts to generate an answer using chat model (env OPENAI_CHAT_MODEL)

Run: python3 rag_app.py
"""
import os
import sys
from pathlib import Path

print('Starting RAG smoke test...')

DATA_PATH = Path('./data/RAG_source.txt')
if not DATA_PATH.exists():
    print('Error: expected data file at ./data/RAG_source.txt')
    sys.exit(1)

# sensible defaults and env overrides
CHUNK_SIZE = int(os.environ.get('RAG_CHUNK_SIZE', 1000))
CHUNK_OVERLAP = int(os.environ.get('RAG_CHUNK_OVERLAP', 0))
K = int(os.environ.get('RAG_RETRIEVER_K', 4))
PERSIST_DIR = os.environ.get('RAG_PERSIST_DIR', './chroma_db')
EMBEDDING_MODEL = os.environ.get('OPENAI_EMBEDDING_MODEL', 'openai.text-embedding-3-small')
CHAT_MODEL = os.environ.get('OPENAI_CHAT_MODEL', 'openai.gpt-5-mini')

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

# load
loader = TextLoader(str(DATA_PATH))
docs = loader.load()
print(f'Loaded {len(docs)} source documents (first 200 chars):')
print(docs[0].page_content[:200].replace('\n',' ') + ('...' if len(docs[0].page_content)>200 else ''))

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
    print(f'[{i}] source={src} snippet="{snippet[:200]}{'...' if len(snippet)>200 else ''}"')

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
