# 🛡️ VanguardRAG — Local Autonomous RAG Pipeline

> **VanguardRAG** is a secure, fully local Retrieval-Augmented Generation system built with **FastAPI, Qdrant, Ollama (Llama 3.2)**, and an interactive **Streamlit** frontend. It ensures absolute data privacy with zero external cloud API dependencies.

---

##  Architecture & Tech Stack

The project runs on **Docker Compose** and consists of 4 isolated microservices:

* **Frontend**: `Streamlit` (interactive dashboard with document upload, session history, and UI controls).
* **Backend API**: `FastAPI` (REST endpoints, document chunking, orchestration between the vector DB and LLM).
* **Vector Database**: `Qdrant` (high-performance semantic similarity search).
* **Local LLM & Embeddings**: `Ollama` running `llama3.2` for text generation and `nomic-embed-text` for vectorization.

---

##  Quick Start

### Prerequisites
* [Docker Desktop](https://www.docker.com/) installed and running.
* Git installed.

### Setup Instructions

1. Clone the repository:
   ```bash
   git clone [https://github.com/cha1btw/VanguardRAG.git](https://github.com/cha1btw/VanguardRAG.git)
   cd VanguardRAG


---

1.	Spin up the entire infrastructure:

docker compose up --build -d



---

2.	Open the apps in your browser:

⚬	Streamlit Frontend UI: http://localhost:8501
⚬	FastAPI Swagger Docs: http://localhost:8000/docs

---

 Key Features

⚬	 Multi-Format Ingestion: Supports .txt, .pdf, and .docx document parsing with automated text chunking.
⚬	 100% Local Inference: Complete data privacy via local model execution using Ollama.
⚬	 Dynamic Context Control: Adjust the top_k chunk retrieval parameter directly from the sidebar UI.
⚬	 Source Citations: Every generated response includes reference links to the source document and chunk index.

----


Repository Structure

VanguardRAG/
├── app/                  # FastAPI backend (routers, services, schemas)
├── frontend/             # Streamlit application (UI logic, Dockerfile)
├── storage/              # Local data volumes for Qdrant & Ollama (git-ignored)
├── docker-compose.yml    # Multi-container orchestration config
└── requirements.txt      # Python dependencies
