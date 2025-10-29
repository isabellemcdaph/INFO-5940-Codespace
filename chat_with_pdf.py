import streamlit as st
import os
from openai import OpenAI
from os import environ
from pathlib import Path

# Support multiple environment variable names and remote base URL used by the template.
api_key = os.environ.get("API_KEY") or os.environ.get("OPENAI_API_KEY")
api_base = os.environ.get("OPENAI_BASE_URL") or os.environ.get("OPENAI_API_BASE") or os.environ.get("OPENAI_BASE") or "https://api.ai.it.cornell.edu"
if not api_key:
    # avoid a hard crash; Streamlit will still load and show a message
    client = None
else:
    client = OpenAI(api_key=api_key, base_url=api_base)

# Optional helpers: langchain splitter/embeddings/Chroma and pypdf for PDFs.
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain.embeddings import OpenAIEmbeddings
    from langchain.vectorstores import Chroma
    LC_AVAILABLE = True
except Exception:
    LC_AVAILABLE = False

try:
    from pypdf import PdfReader
    PYPDF_AVAILABLE = True
except Exception:
    PYPDF_AVAILABLE = False


# Use a wide page layout so columns render side-by-side by default
st.set_page_config(layout="wide")

# Put uploads and settings in the left sidebar (guaranteed left placement)
with st.sidebar:
    st.subheader("Upload files")
    uploaded_files = st.file_uploader(
        "Upload your files (.txt, .md, .pdf)",
        type=("txt", "md", "pdf"),
        accept_multiple_files=True,
    )

# Main area: title and chat
st.title("📝 Isabelle McLeod Daphnis's Assignment 1")
st.subheader("Chat")
question = st.chat_input(
    "Ask something about your uploaded files",
    disabled=not uploaded_files,
)

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Ask something about the uploaded files"}]

# Display the chat history in the main area
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])


def _extract_text_from_uploaded(ufile):
    name = ufile.name
    suffix = Path(name).suffix.lower()
    if suffix in ('.txt', '.md'):
        try:
            return ufile.read().decode('utf-8')
        except Exception:
            return ufile.read().decode('latin-1', errors='ignore')
    if suffix == '.pdf':
        # Try to use pypdf to parse the file-like object
        if PYPDF_AVAILABLE:
            try:
                reader = PdfReader(ufile)
                pages = [p.extract_text() or '' for p in reader.pages]
                return '\n\n'.join(pages)
            except Exception:
                pass
        # fallback: read bytes and try again
        try:
            from pypdf import PdfReader as _PdfReader
            import io
            buf = io.BytesIO(ufile.read())
            reader = _PdfReader(buf)
            pages = [p.extract_text() or '' for p in reader.pages]
            return '\n\n'.join(pages)
        except Exception as e:
            return f'[Could not extract text from PDF: {e}]'
    return ''


if question and uploaded_files:
    # Extract text from each uploaded file
    docs_texts = []
    sources = []
    for up in uploaded_files:
        txt = _extract_text_from_uploaded(up)
        docs_texts.append(txt)
        sources.append(up.name)

    # Append the user's question to the messages
    st.session_state.messages.append({"role": "user", "content": question})
    st.chat_message("user").write(question)

    if client is None:
        st.chat_message("assistant").write("OpenAI client not configured. Set OPENAI_API_KEY or API_KEY and OPENAI_BASE_URL if needed.")
        response = ""
    else:
        CHAT_MODEL = os.environ.get("OPENAI_CHAT_MODEL") or os.environ.get("OPENAI_MODEL") or "gpt-4o"
        EMB_MODEL = os.environ.get("OPENAI_EMBEDDING_MODEL") or "openai.text-embedding-3-small"

        # Build document objects (use langchain Document if available)
        try:
            from langchain_core.documents import Document as LC_Doc
            DocumentClass = LC_Doc
        except Exception:
            try:
                from langchain.schema import Document as LC_Doc
                DocumentClass = LC_Doc
            except Exception:
                class DocumentClass:
                    def __init__(self, page_content, metadata=None):
                        self.page_content = page_content
                        self.metadata = metadata or {}

        documents = [DocumentClass(page_content=t, metadata={'source': s}) for t, s in zip(docs_texts, sources)]

        # Chunk documents
        try:
            splitter = RecursiveCharacterTextSplitter(chunk_size=int(os.environ.get('RAG_CHUNK_SIZE', 1000)), chunk_overlap=int(os.environ.get('RAG_CHUNK_OVERLAP', 0)))
            chunks = splitter.split_documents(documents)
        except Exception:
            chunks = documents

        # Create embeddings + Chroma index (persist to ./chroma_ui)
        try:
            emb = OpenAIEmbeddings(model=EMB_MODEL)
            persist_dir = './chroma_ui'
            vectordb = Chroma.from_documents(documents=chunks, embedding=emb, persist_directory=persist_dir)
        except Exception:
            vectordb = None

        # Retrieval
        if vectordb is not None:
            try:
                retriever = vectordb.as_retriever(search_type='similarity', search_kwargs={'k': int(os.environ.get('RAG_RETRIEVER_K', 4))})
                retrieved = retriever.get_relevant_documents(question)
            except Exception:
                try:
                    retrieved = vectordb.similarity_search(question, k=int(os.environ.get('RAG_RETRIEVER_K', 4)))
                except Exception:
                    retrieved = []
            context_text = '\n\n---\n\n'.join(d.page_content for d in retrieved)
        else:
            context_text = '\n\n---\n\n'.join(t for t in docs_texts)

        # Call OpenAI client
        with st.chat_message("assistant"):
            try:
                prompt_system = (
                    "You are a concise question-answering assistant. Use ONLY the provided context to answer the question. "
                    "Keep answers <= 3 sentences. If unknown, say you do not know.\n\nContext:\n" + context_text
                )
                resp = client.chat.completions.create(
                    model=CHAT_MODEL,
                    messages=[
                        {"role": "system", "content": prompt_system},
                        {"role": "user", "content": question}
                    ],
                )
                try:
                    response = resp.choices[0].message.content
                except Exception:
                    response = str(resp)
                st.write(response)
            except Exception as e:
                response = f"Error calling API: {e}"
                st.chat_message("assistant").write(response)

    # Append the assistant's response to the messages
    st.session_state.messages.append({"role": "assistant", "content": response})