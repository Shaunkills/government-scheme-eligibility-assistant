# SchemeSaathi 🇮🇳

**A Retrieval-Augmented Generation (RAG) application for exploring Indian government schemes and understanding eligibility requirements.**

SchemeSaathi helps users discover relevant government schemes, explore eligibility criteria, and retrieve information from scheme-related documents. It uses semantic search to find relevant source passages and presents them with source information to support more informed decisions.

## 🚀 Features

- **Semantic Search:** Uses sentence-transformer embeddings to retrieve relevant scheme information based on the meaning of a query.
- **Vector Database:** Uses ChromaDB to store and retrieve vector embeddings.
- **PDF Ingestion:** Processes scheme guidelines and extracts useful text for retrieval.
- **Eligibility Assistance:** Helps users explore eligibility criteria, required documents, and scheme-related information.
- **Source-Based Responses:** Returns relevant retrieved passages to help users verify information against source material.
- **Web Interface:** Provides an interactive Streamlit frontend.
- **REST API:** Uses FastAPI to expose scheme retrieval and question-answering endpoints.

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Frontend | Streamlit |
| Backend | FastAPI |
| Embeddings | Sentence Transformers |
| Embedding Model | `sentence-transformers/all-MiniLM-L6-v2` |
| Vector Database | ChromaDB |
| PDF Processing | PyPDF |
| Language | Python |

## 🧠 How It Works

1. **Document ingestion:** Scheme guidelines and structured scheme data are processed into text chunks.
2. **Embedding generation:** The sentence-transformer model converts text chunks into vector embeddings.
3. **Vector storage:** ChromaDB stores the embeddings for semantic retrieval.
4. **User query:** A user asks a question about a government scheme or eligibility requirement.
5. **Semantic retrieval:** The query is matched against relevant stored information using vector similarity.
6. **Source-based output:** The application displays relevant passages and available source details so users can inspect the retrieved information.

> **Current implementation:** The application uses embedding-based semantic retrieval and ChromaDB. It returns retrieved source passages rather than relying on an LLM to generate a fully synthesized answer.

## 📁 Project Structure

```text
government-scheme-eligibility-assistant/
├── app/
│   ├── __init__.py
│   ├── ingestion.py
│   └── main.py
├── data/
│   ├── processed/
│   │   └── scheme_chunks.json
│   ├── raw/
│   │   └── top_class_sc_students_2026_27.pdf
│   └── schemes.json
├── tests/
│   └── test_api.py
├── frontend.py
├── requirements.txt
├── render.yaml
├── .gitignore
└── README.md
```

## ⚙️ Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/government-scheme-eligibility-assistant.git
cd government-scheme-eligibility-assistant
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the FastAPI backend

```bash
uvicorn app.main:app --reload
```

The backend will usually be available at:

- API: `http://127.0.0.1:8000`
- Interactive API documentation: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/health`

### 5. Start the Streamlit frontend

Open a second terminal, activate the same virtual environment, and run:

```bash
streamlit run frontend.py
```

The Streamlit application will display its local URL in the terminal.

## 🔌 API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Backend information |
| GET | `/health` | Health check |
| GET | `/schemes` | Retrieve available schemes |
| POST | `/ask` | Retrieve relevant information for a question |

Refer to `/docs` for the request and response schemas.

## ☁️ Deployment

The project is designed to use separate services for the frontend and backend:

- **Backend:** Render
- **Frontend:** Streamlit Community Cloud

Configure the frontend's `SCHEMESAATHI_API_URL` environment variable or Streamlit secret to point to the deployed FastAPI backend.

Free hosting availability, resource limits, and service-sleep behavior depend on the hosting provider's current policies.

## 🔮 Future Improvements

- Integrate an LLM to synthesize retrieved passages into conversational answers.
- Add citations linking responses to specific source documents and page numbers.
- Expand the scheme dataset across more government departments and eligibility categories.
- Add multilingual support for Indian languages.
- Add automated tests for retrieval quality and eligibility-related queries.

## ⚠️ Disclaimer

SchemeSaathi is an informational assistant, not an official government service. Scheme guidelines can change. Users should verify eligibility, deadlines, and application requirements against the latest official government documents before applying.

## 👨‍💻 Author

Developed as a practical project exploring semantic search, embeddings, vector databases, document retrieval, and API-based AI applications.
