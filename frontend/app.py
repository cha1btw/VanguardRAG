import os
import time
from urllib.parse import quote

import requests
import streamlit as st

API_URL = os.getenv(
    "API_URL", "http://api:8000/api/v1/documents"
).rstrip("/")
API_BASE_URL = os.getenv(
    "API_BASE_URL", API_URL.split("/api/v1/")[0]
).rstrip("/")
API_REQUEST_TIMEOUT = (5, 300)
MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024
HEALTH_CACHE_SECONDS = 15
STARTER_PROMPTS = [
    "Summarize the key points",
    "What are the main risks?",
    "List important dates",
]

st.set_page_config(
    page_title="VanguardRAG — Local AI Assistant",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Colors come from the Streamlit theme (.streamlit/config.toml) via CSS variables.
st.markdown(
    """
    <style>
    .stChatMessage {
        border-radius: 12px;
        padding: 14px;
        margin-bottom: 10px;
    }
    .stButton button, .stDownloadButton button {
        border-radius: 8px;
        font-weight: 600;
    }
    .hero-box {
        background: linear-gradient(
            135deg, var(--secondary-background-color) 0%, var(--background-color) 100%
        );
        border: 1px solid rgba(148, 163, 184, 0.25);
        padding: 24px;
        border-radius: 16px;
        margin-bottom: 24px;
    }
    .hero-box h2 { margin: 0 0 8px 0; padding: 0; }
    .hero-box p { color: #9ca3af; font-size: 16px; margin: 0 0 16px 0; }
    .hero-steps { display: flex; flex-wrap: wrap; gap: 12px 24px; }
    .step-badge {
        background-color: var(--primary-color);
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
        margin-right: 6px;
    }
    .status-pill {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 999px;
        font-size: 13px;
        font-weight: 600;
    }
    .status-ok { background: rgba(34, 197, 94, 0.15); color: #4ade80; }
    .status-down { background: rgba(239, 68, 68, 0.15); color: #f87171; }
    </style>
""",
    unsafe_allow_html=True,
)


def describe_error(response):
    """Return a short human-readable reason from a failed API response."""
    try:
        detail = response.json().get("detail")
    except (ValueError, AttributeError):
        detail = None
    if isinstance(detail, list):
        # FastAPI validation errors: [{"loc": [...], "msg": "..."}]
        detail = "; ".join(str(item.get("msg", item)) for item in detail)
    return f"{detail or response.text or 'no details'} (HTTP {response.status_code})"


@st.cache_data(ttl=HEALTH_CACHE_SECONDS, show_spinner=False)
def check_api_health():
    """Return (is_online, message). Cached so reruns do not hit the API each time."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
    except requests.RequestException:
        return False, "Cannot reach the API"
    if response.ok:
        return True, "API online"
    return False, describe_error(response)


def load_documents():
    """Fetch indexed documents into session state; keep the error if it fails."""
    try:
        response = requests.get(API_URL, timeout=API_REQUEST_TIMEOUT)
        if response.ok:
            st.session_state.documents = response.json()
            st.session_state.documents_error = None
        else:
            st.session_state.documents = []
            st.session_state.documents_error = describe_error(response)
    except requests.RequestException as error:
        st.session_state.documents = []
        st.session_state.documents_error = f"Could not load documents: {error}"


def format_citation_title(citation):
    title = (
        f"**{citation.get('document_name', 'Unknown')}** · "
        f"chunk #{citation.get('chunk_index', '?')}"
    )
    if citation.get("score") is not None:
        title += f" · relevance {citation['score']:.2f}"
    return title


def delete_document(document_name):
    """Delete a document via the API. Returns an error message or None."""
    try:
        response = requests.delete(
            f"{API_URL}/{quote(document_name, safe='')}",
            timeout=API_REQUEST_TIMEOUT,
        )
    except requests.RequestException as error:
        return f"Backend connection failed: {error}"
    # 404 means it is already gone, which is the state the user wanted.
    if response.ok or response.status_code == 404:
        return None
    return f"Delete failed: {describe_error(response)}"


def render_sources(citations):
    with st.expander(f"📚 Sources ({len(citations)})"):
        for citation in citations:
            st.markdown(format_citation_title(citation))
            excerpt = citation.get("content", "").strip()
            if excerpt:
                st.caption(excerpt)


def render_message(message):
    st.markdown(message["content"])
    if message.get("citations"):
        render_sources(message["citations"])
    elif "citations" in message:
        st.caption("No matching fragments found in the documents.")
    if message.get("elapsed"):
        st.caption(f"Generated in {message['elapsed']:.1f} s")


def export_chat(messages):
    parts = []
    for message in messages:
        text = f"## {message['role'].capitalize()}\n\n{message['content']}"
        for citation in message.get("citations") or []:
            text += (
                f"\n\n> {format_citation_title(citation)}: "
                f"{citation.get('content', '').strip()}"
            )
        parts.append(text)
    return "\n\n".join(parts)


for key, default in (
    ("documents", None),
    ("documents_error", None),
    ("messages", []),
    ("uploader_key", 0),
    ("flash", None),
    ("pending_delete", None),
):
    if key not in st.session_state:
        st.session_state[key] = default

if st.session_state.flash:
    st.toast(st.session_state.flash, icon="✅")
    st.session_state.flash = None

# --- SIDEBAR (STATUS, DOCUMENTS, SETTINGS) ---
with st.sidebar:
    st.title("🛡️ VanguardRAG")
    st.caption("🔒 Fully private local RAG")

    api_online, api_message = check_api_health()
    status_column, refresh_column = st.columns([4, 1], vertical_alignment="center")
    status_column.markdown(
        f"<span class='status-pill {'status-ok' if api_online else 'status-down'}'>"
        f"● {api_message}</span>",
        unsafe_allow_html=True,
    )
    if refresh_column.button("↻", help="Re-check API connection", key="recheck_api"):
        check_api_health.clear()
        st.rerun()
    st.divider()

    st.subheader("📁 Knowledge base")
    uploaded_file = st.file_uploader(
        "Upload a .txt, .md, .pdf or .docx file (up to 10 MiB)",
        type=["txt", "md", "pdf", "docx"],
        key=f"uploader_{st.session_state.uploader_key}",
    )

    if uploaded_file is not None:
        upload_too_large = uploaded_file.size > MAX_UPLOAD_SIZE_BYTES
        if upload_too_large:
            st.error(
                f"{uploaded_file.size / 1024 / 1024:.1f} MiB is too large. "
                "Files must be 10 MiB or smaller."
            )
        if st.button(
            "🚀 Ingest document",
            type="primary",
            use_container_width=True,
            disabled=upload_too_large or not api_online,
            help=None if api_online else "The API is offline.",
        ):
            with st.spinner("Reading, chunking, and vectorizing..."):
                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        uploaded_file.type,
                    )
                }
                try:
                    response = requests.post(
                        f"{API_URL}/ingest",
                        files=files,
                        timeout=API_REQUEST_TIMEOUT,
                    )
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.flash = (
                            f"Added {data.get('total_chunks', 0)} chunks from "
                            f"{data.get('filename', uploaded_file.name)}."
                        )
                        st.session_state.documents = None
                        # A new widget key clears the selected file.
                        st.session_state.uploader_key += 1
                        st.rerun()
                    else:
                        st.error(f"Ingest failed: {describe_error(response)}")
                except requests.RequestException as error:
                    st.error(f"Backend connection failed: {error}")

    if st.session_state.documents is None:
        load_documents()

    header_column, reload_column = st.columns([4, 1], vertical_alignment="center")
    header_column.markdown(
        f"**Indexed documents** ({len(st.session_state.documents)})"
    )
    if reload_column.button("↻", help="Reload document list", key="reload_docs"):
        load_documents()
        st.rerun()

    if st.session_state.documents_error:
        st.warning(st.session_state.documents_error)
    elif st.session_state.documents:
        for index, document in enumerate(st.session_state.documents):
            name_column, delete_column = st.columns(
                [5, 1], vertical_alignment="center"
            )
            name_column.caption(
                f"📄 `{document['document_name']}` · "
                f"{document['chunks_count']} "
                f"chunk{'s' if document['chunks_count'] != 1 else ''}"
            )
            if delete_column.button(
                "🗑️",
                key=f"delete_{index}",
                help=f"Delete {document['document_name']}",
            ):
                st.session_state.pending_delete = document["document_name"]

        pending_delete = st.session_state.pending_delete
        if pending_delete in [
            d["document_name"] for d in st.session_state.documents
        ]:
            st.warning(
                f"Delete `{pending_delete}` from the knowledge base? "
                "This cannot be undone."
            )
            confirm_column, cancel_column = st.columns(2)
            if confirm_column.button(
                "Delete", type="primary", use_container_width=True
            ):
                error = delete_document(pending_delete)
                if error:
                    st.error(error)
                else:
                    st.session_state.flash = f"Deleted {pending_delete}."
                    st.session_state.pending_delete = None
                    st.session_state.documents = None
                    st.rerun()
            if cancel_column.button("Cancel", use_container_width=True):
                st.session_state.pending_delete = None
                st.rerun()
    else:
        st.caption("Nothing indexed yet. Upload a file to get started.")

    st.divider()
    st.subheader("⚙️ Search settings")
    top_k = st.slider(
        "Context window (chunks)",
        min_value=1,
        max_value=10,
        value=3,
        help="Number of relevant document fragments passed to the LLM.",
    )
    minimum_score = st.slider(
        "Minimum relevance",
        min_value=0.0,
        max_value=1.0,
        value=0.0,
        step=0.05,
        help="Filter out document fragments below this similarity score. "
        "0 disables the filter.",
    )

    st.divider()
    clear_column, export_column = st.columns(2)
    if clear_column.button(
        "🗑️ Clear",
        use_container_width=True,
        disabled=not st.session_state.messages,
        help="Clear chat history",
    ):
        st.session_state.messages = []
        st.rerun()
    export_column.download_button(
        "⬇️ Export",
        data=export_chat(st.session_state.messages),
        file_name="vanguardrag-chat.md",
        mime="text/markdown",
        use_container_width=True,
        disabled=not st.session_state.messages,
        help="Download the conversation as Markdown",
    )

    st.markdown(
        "<p style='text-align: center; color: gray; font-size: 12px; margin-top: 16px;'>"
        "Powered by Ollama (llama3.2) & Qdrant</p>",
        unsafe_allow_html=True,
    )


# --- MAIN PAGE (HERO & CHAT) ---
selected_prompt = None

if not st.session_state.messages:
    st.markdown(
        """
        <div class="hero-box">
            <h2>🛡️ Welcome to VanguardRAG</h2>
            <p>
                Your personal autonomous intelligence for internal documents.
                All data stays strictly on your machine and runs locally.
            </p>
            <div class="hero-steps">
                <div><span class="step-badge">1</span>Upload a file on the left</div>
                <div><span class="step-badge">2</span>Ask a question in chat</div>
                <div><span class="step-badge">3</span>Get answers with citations</div>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )
    if not st.session_state.documents and not st.session_state.documents_error:
        st.info("No documents indexed yet. Upload a file in the sidebar to begin.")
    st.caption("Try a question")
    for column, starter in zip(st.columns(len(STARTER_PROMPTS)), STARTER_PROMPTS):
        if column.button(starter, use_container_width=True):
            selected_prompt = starter

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        render_message(message)

if prompt := (
    st.chat_input("Type your question about the documents...")
    or selected_prompt
):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🔍 Searching documents and generating response..."):
            try:
                payload = {
                    "query": prompt,
                    "top_k": top_k,
                    "score_threshold": minimum_score or None,
                }
                started_at = time.perf_counter()
                response = requests.post(
                    f"{API_URL}/generate",
                    json=payload,
                    timeout=API_REQUEST_TIMEOUT,
                )
                elapsed_seconds = time.perf_counter() - started_at

                if response.status_code == 200:
                    res_data = response.json()
                    reply = {
                        "role": "assistant",
                        "content": res_data.get("answer", "No answer provided"),
                        "citations": res_data.get("citations", []),
                        "elapsed": elapsed_seconds,
                    }
                    render_message(reply)
                else:
                    reply = {
                        "role": "assistant",
                        "content": f"⚠️ Generation error: {describe_error(response)}",
                    }
                    st.error(reply["content"])
            except requests.RequestException as error:
                reply = {
                    "role": "assistant",
                    "content": f"⚠️ API connection error: {error}",
                }
                st.error(reply["content"])
        st.session_state.messages.append(reply)
    # Rerun so sidebar buttons (clear/export) reflect the new history.
    st.rerun()
