import requests
import streamlit as st

API_URL = "http://api:8000/api/v1/documents"

st.set_page_config(
    page_title="VanguardRAG — Локальный ИИ-ассистент",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Расширенные стили для красивого и понятного UI
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

# --- БОКОВАЯ ПАНЕЛЬ (УПРАВЛЕНИЕ) ---
with st.sidebar:
    st.image(
        "https://img.icons8.com/color/96/artificial-intelligence.png", width=64
    )
    st.title("VanguardRAG")
    st.caption("🔒 Полностью конфиденциальный RAG")
    st.divider()

    st.subheader("📁 Шаг 1: База знаний")
    st.markdown(
        "Загрузите текстовый файл, PDF или документ Word, чтобы ИИ мог опираться на них."
    )

    uploaded_file = st.file_uploader(
        "Выберите файл", type=["txt", "pdf", "docx"]
    )

    if uploaded_file is not None:
        if st.button(
            "🚀 Индексировать документ", type="primary", use_container_width=True
        ):
            with st.spinner("Читаем, режем на чанки и векторизуем..."):
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
                            f"Успешно! Добавлено фрагментов: {data.get('chunks_count')}"
                        )
                    else:
                        st.error(f"Ошибка: {response.text}")
                except Exception as e:
                    st.error(f"Нет связи с бэкендом: {e}")

    st.divider()
    st.subheader("⚙️ Шаг 2: Настройка поиска")
    top_k = st.slider(
        "Объем контекста (чанкам)",
        min_value=1,
        max_value=10,
        value=3,
        help="Сколько релевантных фрагментов документа передавать нейросети для ответа.",
    )

    st.divider()
    if st.button("🗑️ Очистить диалог", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: gray; font-size: 12px;'>Работает на Ollama (llama3.2) & Qdrant</p>",
        unsafe_allow_html=True,
    )


# --- ОСНОВНАЯ ОБРАЗЦОВАЯ СТРАНИЦА ---

# Приветственный блок (Hero Section) для мгновенного понимания сути
st.markdown(
    """
    <div class="hero-box">
        <h2>🛡️ Добро пожаловать в VanguardRAG!</h2>
        <p style='color: #9ca3af; font-size: 16px; margin-bottom: 12px;'>
            Это ваш личный автономный интеллект для работы с внутренними документами. 
            Данные не покидают ваш компьютер и обрабатываются локально.
        </p>
        <div style='display: flex; gap: 16px; margin-top: 12px;'>
            <div><span class="step-badge">1</span> Загрузите файл слева</div>
            <div><span class="step-badge">2</span> Задайте вопрос в чате</div>
            <div><span class="step-badge">3</span> Получите точный ответ с цитатами</div>
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

# Инициализация истории чата
if "messages" not in st.session_state:
    st.session_state.messages = []

# Стартовое сообщение ассистента
if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown(
            "👋 Привет! Я готов к работе. Загрузите документ в панели слева (или просто задайте общий вопрос), и я помогу вам разобраться."
        )

# Отрисовка истории сообщений
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Обработка ввода пользователя
if prompt := st.chat_input("Напишите ваш вопрос по документам..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🔍 Ищу информацию в документах и формирую ответ..."):
            try:
                payload = {"query": prompt, "top_k": top_k}
                response = requests.post(f"{API_URL}/generate", json=payload)

                if response.status_code == 200:
                    res_data = response.json()
                    answer = res_data.get("answer", "Нет ответа")
                    citations = res_data.get("citations", [])

                    full_response = f"{answer}\n\n---\n**📚 Использованные источники:**\n"
                    if citations:
                        for cit in citations:
                            full_response += f"- *{cit['document_name']} (фрагмент #{cit['chunk_index']})*\n"
                    else:
                        full_response += (
                            "- *Прямые совпадения в базе не зафиксированы*\n"
                        )

                    st.markdown(full_response)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": full_response}
                    )
                else:
                    err_msg = f"Ошибка генерации ответа: {response.text}"
                    st.error(err_msg)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": err_msg}
                    )
            except Exception as e:
                err_msg = f"Не удалось связаться с бэкенд-сервером: {e}"
                st.error(err_msg)
                st.session_state.messages.append(
                    {"role": "assistant", "content": err_msg}
                )
