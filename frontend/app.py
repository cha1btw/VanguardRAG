import requests
import streamlit as st

API_URL = "http://api:8000/api/v1/documents"

st.set_page_config(
    page_title="VanguardRAG — Корпоративный ассистент", layout="wide"
)

st.title("🛡️ VanguardRAG")
st.caption(
    "Локальная автономная система поиска и генерации данных (Mac + Docker + Ollama + Qdrant)"
)

# Садбар для управления и загрузки
with st.sidebar:
    st.header("📂 База знаний")
    uploaded_file = st.file_uploader(
        "Загрузить документ (.txt, .pdf, .docx)", type=["txt", "pdf", "docx"]
    )

    if uploaded_file is not None:
        if st.button("Индексировать документ", type="primary"):
            with st.spinner("Обработка и векторизация..."):
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
                            f"Успешно! Загружено чанков: {data.get('chunks_count')}"
                        )
                    else:
                        st.error(f"Ошибка сервера: {response.text}")
                except Exception as e:
                    st.error(f"Не удалось подключиться к API: {e}")

    st.divider()
    st.header("⚙️ Параметры поиска")
    top_k = st.slider(
        "Количество чанков (контекст)", min_value=1, max_value=10, value=3
    )

    if st.button("🗑️ Очистить историю чата"):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.markdown("### О системе")
    st.info(
        "Все данные обрабатываются локально. Модели: `nomic-embed-text` & `llama3.2`."
    )

# Основная область чата
st.subheader("💬 Диалог с документами")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Задайте вопрос по вашим документам..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Генерация ответа с цитатами..."):
            try:
                payload = {"query": prompt, "top_k": top_k}
                response = requests.post(f"{API_URL}/generate", json=payload)

                if response.status_code == 200:
                    res_data = response.json()
                    answer = res_data.get("answer", "Нет ответа")
                    citations = res_data.get("citations", [])

                    full_response = f"{answer}\n\n**📚 Источники:**\n"
                    if citations:
                        for idx, cit in enumerate(citations):
                            full_response += f"- *{cit['document_name']} (Чанк #{cit['chunk_index']})*\n"
                    else:
                        full_response += (
                            "- *Прямые совпадения в базе не найдены*\n"
                        )

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
                err_msg = f"Ошибка соединения с бэкендом: {e}"
                st.error(err_msg)
                st.session_state.messages.append(
                    {"role": "assistant", "content": err_msg}
                )
