# 🛡️ VanguardRAG — Local Autonomous RAG Pipeline

> **VanguardRAG** is a secure, fully local Retrieval-Augmented Generation system built with **FastAPI, Qdrant, Ollama (Llama 3.2)**, and an interactive **Streamlit** frontend. It ensures absolute data privacy with zero external cloud API dependencies.

---

## Architecture & Tech Stack

The project runs on **Docker Compose** and consists of 4 isolated services:

* **Frontend**: `Streamlit` (document upload, chat, sources, and search settings).
* **Backend API**: `FastAPI` (REST endpoints, document chunking, orchestration between the vector DB and LLM).
* **Vector Database**: `Qdrant` (semantic similarity search).
* **Local LLM & Embeddings**: `Ollama` running `llama3.2` for text generation and `nomic-embed-text` for vectorization.

---

## Quick Start

### Prerequisites
* [Docker Desktop](https://www.docker.com/) (Docker Compose 2.24+).
* Git.

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/cha1btw/VanguardRAG.git
   cd VanguardRAG
   ```

2. Start all services:
   ```bash
   docker compose up --build -d
   ```

3. Download the models into Ollama (first run only, about 2 GB):
   ```bash
   docker compose exec ollama ollama pull llama3.2
   docker compose exec ollama ollama pull nomic-embed-text
   ```

4. Open the apps in your browser:
   * Streamlit UI: http://localhost:8501
   * FastAPI Swagger docs: http://localhost:8000/docs

Configuration is optional. See `.env.example` for the available overrides.

---

## Key Features

* **Multi-format ingestion**: `.txt`, `.md`, `.pdf`, and `.docx` files with automated text chunking (10 MiB limit).
* **100% local inference**: complete data privacy via local models running in Ollama.
* **Dynamic context control**: tune the number of retrieved chunks and the minimum relevance from the sidebar.
* **Source citations**: every answer lists the document and chunk it came from.

---

## Repository Structure

```
VanguardRAG/
├── app/                  # FastAPI backend (routers, services, schemas)
├── frontend/             # Streamlit application (UI logic, Dockerfile)
├── storage/              # Local data volumes for Qdrant & Ollama (git-ignored)
├── docker-compose.yml    # Multi-container orchestration config
└── requirements.txt      # Backend Python dependencies
```
