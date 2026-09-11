import requests
import streamlit as st

API_URL = "http://api:8000/api/v1/documents"

st.set_page_config(
    page_title="VanguardRAG — AI Assistant",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Кастомные стили для аккуратного и современного UI
st.markdown(
    """
    <style>
    .main {
        background-color: #0e1117;
    }
    .stChatMessage {
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 10px;
    }
    .stButton button {
        border-radius: 8px;
        font-weight: 500;
    }
    .sidebar .stSidebarContent {
        background-color: #161b22;
    }
    h1 {
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Шапка приложения
st.title("🛡️ VanguardRAG")
st.caption(
    "Автономная корпоративная система поиска и генерации данных (Fully Local & Private)"
)
st.divider()

# Садбар для управления и загрузки
with st.sidebar:
    st.header("📂 База знаний")
    uploaded_file = st.file_uploader(
        "Загрузить документ",
        type=["txt", "pdf", "docx"],
        help="Поддерживаются файлы TXT, PDF и DOCX",
    )

    if uploaded_file is not None:
        if st.button("🚀 Индексировать документ", type="primary", use_container_width=True):
            with st.spinner("Обработка, чанкинг и векторизация..."):
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
                            f"Готово! Чанков создано: {data.get('chunks_count')}"
                        )
                    else:
                        st.error(f"Ошибка сервера: {response.text}")
                except Exception as e:
                    st.error(f"Нет связи с бэкендом: {e}")

    st.divider()
    st.header("⚙️ Параметры")
    top_k = st.slider(
        "Контекст (chunks)", min_value=1, max_value=10, value=3
    )

    if st.button("🗑️ Очистить историю чата", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.markdown("### Стек технологий")
    st.markdown(
        "- **LLM:** `llama3.2` (Ollama)\n- **Embeddings:** `nomic-embed-text`\n- **DB:** Qdrant Vector Search"
    )

# Основная область чата
if "messages" not in st.session_state:
    st.session_state.messages = []

# Приветственное сообщение, если чат пустой
if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown(
            "Привет! Я твой локальный AI-ассистент. Загрузи документ через боковую панель слева и задавай по нему любые вопросы."
        )

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Напишите ваш вопрос..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Анализирую документы и генерирую ответ..."):
            try:
                payload = {"query": prompt, "top_k": top_k}
                response = requests.post(f"{API_URL}/generate", json=payload)

                if response.status_code == 200:
                    res_data = response.json()
                    answer = res_data.get("answer", "Нет ответа")
                    citations = res_data.get("citations", [])

                    full_response = f"{answer}\n\n---\n**📚 Источники:**\n"
                    if citations:
                        for cit in citations:
                            full_response += f"- *{cit['document_name']} (Чанк #{cit['chunk_index']})*\n"
                    else:
                        full_response += "- *Прямые совпадения не найдены*\n"

                    st.markdown(full_response)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": full_response}
                    )
                else:
                    err_msg = f"Ошибка генерации: {response.text}"
                    st.error(err_msg)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": err_msg}
                    )
            except Exception as e:
                err_msg = f"Ошибка подключения к API: {e}"
                st.error(err_msg)
                st.session_state.messages.append(
                    {"role": "assistant", "content": err_msg}
                )
