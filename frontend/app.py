import requests
import streamlit as st

API_URL = "http://api:8000/api/v1/documents"

st.set_page_config(
    page_title="VanguardRAG — Local AI Assistant",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .main {
        background-color: #0e1117;
    }
    .stChatMessage {
        border-radius: 12px;
        padding: 14px;
        margin-bottom: 10px;
    }
    .stButton button {
        border-radius: 8px;
        font-weight: 600;
    }
    .hero-box {
        background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
        border: 1px solid #374151;
        padding: 24px;
        border-radius: 16px;
        margin-bottom: 24px;
    }
    .step-badge {
        background-color: #3b82f6;
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- SIDEBAR (CONTROLS & UPLOAD) ---
with st.sidebar:
    st.image(
        "https://img.icons8.com/color/96/artificial-intelligence.png", width=64
    )
    st.title("VanguardRAG")
    st.caption("🔒 Fully Private Local RAG")
    st.divider()

    st.subheader("📁 Step 1: Knowledge Base")
    st.markdown(
        "Upload text files, PDFs, or Word documents so the AI can reference them."
    )

    uploaded_file = st.file_uploader(
        "Choose a file", type=["txt", "pdf", "docx"]
    )

    if uploaded_file is not None:
        if st.button(
            "🚀 Ingest Document", type="primary", use_container_width=True
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
                    response = requests.post(f"{API_URL}/ingest", files=files)
                    if response.status_code == 200:
                        data = response.json()
                        st.success(
                            f"Success! Chunks added: {data.get('chunks_count')}"
                        )
                    else:
                        st.error(f"Error: {response.text}")
                except Exception as e:
                    st.error(f"Backend connection failed: {e}")

    st.divider()
    st.subheader("⚙️ Step 2: Search Settings")
    top_k = st.slider(
        "Context Window (Chunks)",
        min_value=1,
        max_value=10,
        value=3,
        help="Number of relevant document fragments passed to the LLM.",
    )

    st.divider()
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: gray; font-size: 12px;'>Powered by Ollama (llama3.2) & Qdrant</p>",
        unsafe_allow_html=True,
    )


# --- MAIN PAGE (HERO & CHAT) ---

st.markdown(
    """
    <div class="hero-box">
        <h2>🛡️ Welcome to VanguardRAG!</h2>
        <p style='color: #9ca3af; font-size: 16px; margin-bottom: 12px;'>
            Your personal autonomous intelligence for internal documents. 
            All data stays strictly on your machine and runs locally.
        </p>
        <div style='display: flex; gap: 16px; margin-top: 12px;'>
            <div><span class="step-badge">1</span> Upload file on the left</div>
            <div><span class="step-badge">2</span> Ask a question in chat</div>
            <div><span class="step-badge">3</span> Get precise answers with citations</div>
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown(
            "👋 Hello! I am ready. Upload a document in the left sidebar (or ask a general question) and I will help you analyze it."
        )

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Type your question about the documents..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner(
            "🔍 Searching documents and generating response..."
        ):
            try:
                payload = {"query": prompt, "top_k": top_k}
                response = requests.post(f"{API_URL}/generate", json=payload)

                if response.status_code == 200:
                    res_data = response.json()
                    answer = res_data.get("answer", "No answer provided")
                    citations = res_data.get("citations", [])

                    full_response = f"{answer}\n\n---\n**📚 Sources Used:**\n"
                    if citations:
                        for cit in citations:
                            full_response += f"- *{cit['document_name']} (Chunk #{cit['chunk_index']})*\n"
                    else:
                        full_response += (
                            "- *No direct matches found in vector DB*\n"
                        )

                    st.markdown(full_response)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": full_response}
                    )
                else:
                    err_msg = f"Generation error: {response.text}"
                    st.error(err_msg)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": err_msg}
                    )
            except Exception as e:
                err_msg = f"API connection error: {e}"
                st.error(err_msg)
                st.session_state.messages.append(
                    {"role": "assistant", "content": err_msg}
                )
