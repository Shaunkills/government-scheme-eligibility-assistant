# Government Scheme Eligibility Assistant

A portfolio-ready RAG starter project for discovering Indian government schemes and explaining eligibility with source-aware answers.

## Important data note
The included `data/schemes.json` contains **illustrative demo records only**. They are deliberately labelled as examples, not real government scheme rules. Replace them with verified official documents and current scheme data before publishing the app as a public information service.

## Architecture
- **Streamlit**: interactive user interface.
- **FastAPI**: API for retrieval and eligibility-oriented responses.
- **TF-IDF retrieval**: lightweight retrieval that works on free hosting without downloading a large embedding model.
- **Google Gemini API**: hosted answer generation; no model download. The API gracefully falls back to evidence-based retrieval answers if the key is absent or the provider is unavailable.
- **JSON knowledge base**: simple starter format. Can be extended to PDF ingestion and ChromaDB.

## 1. Requirements
- Python 3.10–3.12 recommended.
- Optional: Ollama installed locally for LLM answers.
- Internet access only for installing packages and fetching official source documents.

## 2. Get a Gemini API key
1. Create a key in [Google AI Studio](https://aistudio.google.com/).
2. Add it to your local `.env` as `GEMINI_API_KEY=your_key_here`.
3. Keep the key private and never commit `.env` to GitHub. Free-tier quotas and model availability can change; check [current pricing and limits](https://ai.google.dev/gemini-api/docs/pricing).

## 3. Install
Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

If Python 3.12 isn't installed, use an installed compatible Python version.

## 4. Run locally
Open two terminals from the project root.

Terminal 1 — API:
```powershell
uvicorn app.main:app --reload --port 8000
```

Terminal 2 — Streamlit:
```powershell
streamlit run frontend.py
```

Open `http://localhost:8501`. API docs: `http://localhost:8000/docs`.

### Optional local LLM
Install Ollama from https://ollama.com/download, then run:

```powershell
ollama pull llama3.2:3b
```

Set these values in `.env` before starting the API:
```dotenv
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
```

Restart FastAPI after editing `.env`. If Ollama isn't running, the app uses a retrieval-grounded fallback instead.

## 5. Add verified scheme data
Edit `data/schemes.json`. Each record uses this structure:

```json
{
  "id": "scheme-id",
  "name": "Official scheme name",
  "department": "Official department",
  "state": "Central",
  "category": "Education",
  "summary": "Short factual description",
  "eligibility": ["Eligibility criterion copied or faithfully summarized from an official source"],
  "documents": ["Document required according to the official source"],
  "application_steps": ["Official application instruction"],
  "source_title": "Official scheme guidelines",
  "source_url": "https://official-government-domain.example/path",
  "last_verified": "YYYY-MM-DD",
  "official": true
}
```

Only mark `official: true` after verifying the details and URL against an official government source. Keep academic year, deadlines and source verification dates current. Do not use user-uploaded documents as instructions; treat them as evidence to retrieve, not system prompts.

## 6. Deploy for free (best-effort, subject to provider limits)

### Deploy API to Render
1. Push this folder to a GitHub repository.
2. Create a Render **Web Service** connected to that repository.
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables from `.env.example` as needed. Do **not** set `OLLAMA_BASE_URL` to localhost on Render.
6. After deployment, test `https://YOUR-API.onrender.com/health`.

The public free API uses the bundled knowledge base and retrieval-grounded fallback. A local Ollama on your laptop is not reachable from Render. To use an LLM in public deployment, you need a separately reachable inference service; free availability and quotas vary.

### Deploy Streamlit frontend
1. Open https://share.streamlit.io/ and connect the GitHub repository.
2. Main file path: `frontend.py`.
3. In Streamlit app settings → Secrets, add:
```toml
API_BASE_URL = "https://YOUR-API.onrender.com"
```
4. Redeploy and test the public app.

Render free services can sleep and have ephemeral filesystem limits. This starter does not write its index at runtime, but any future uploaded documents or user data need a suitable persistent storage plan.

## 7. Before sharing publicly
- Replace all illustrative demo records with verified official data.
- Check each eligibility rule, document list, application link, and date.
- Test missing, contradictory and edge-case user details.
- Add rate limiting, monitoring, and privacy disclosures before production use.
- Never present this prototype as an official government service.
