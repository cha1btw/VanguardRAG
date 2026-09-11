# 🛡️ VanguardRAG — Local Autonomous RAG Pipeline

> **VanguardRAG** — это защищенная локальная система поиска и генерации данных (Retrieval-Augmented Generation), развернутая на базе связки **FastAPI, Qdrant, Ollama (Llama 3.2)** и интерактивного **Streamlit**-интерфейса. Полностью автономное решение без утечки данных во внешние облачные API.

---

## 🏗️ Архитектура и стек технологий

Проект полностью упакован в **Docker Compose** и состоит из 4 изолированных сервисов:

* **Frontend**: `Streamlit` (красивый асинхронный UI с виджетами, панелью загрузки документов и историей чата).
* **Backend API**: `FastAPI` (обработка файлов, чанкинг, оркестрация запросов к базе векторов и LLM).
* **Vector Database**: `Qdrant` (быстрый поиск релевантных фрагментов по эмбеддингам).
* **Local LLM & Embeddings**: `Ollama` (модели `llama3.2` для генерации текста и `nomic-embed-text` для векторизации).

---

## 🚀 Быстрый старт (Запуск за 1 минуту)

### Требования
* Установленный [Docker Desktop](https://www.docker.com/)
* Установленный Git

### Инструкция по запуску:
1. Клонируйте репозиторий:
   ```bash
   git clone [https://github.com/cha1btw/VanguardRAG.git](https://github.com/cha1btw/VanguardRAG.git)
   cd VanguardRAG
