import json
import os
from pathlib import Path
from typing import Any, Optional

import chromadb
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
# SentenceTransformer is imported lazily inside get_embedding_model()
# to reduce startup work for the web service.


# ==================================================
# CONFIGURATION
# ==================================================

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

SCHEMES_PATH = Path(
    os.getenv("SCHEMES_PATH", "data/schemes.json")
)

if not SCHEMES_PATH.is_absolute():
    SCHEMES_PATH = ROOT / SCHEMES_PATH

CHUNKS_PATH = ROOT / "data" / "processed" / "scheme_chunks.json"
CHROMA_PATH = ROOT / "data" / "chroma_db"

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
COLLECTION_NAME = "government_schemes"

DISCLAIMER = (
    "This is a prototype for informational purposes only. "
    "It is not an official government service or a confirmed "
    "eligibility decision. Verify current scheme guidelines "
    "and deadlines with the relevant official department."
)

app = FastAPI(
    title="Government Scheme Eligibility Assistant API",
    description=(
        "A government scheme information assistant using "
        "Hugging Face embeddings and ChromaDB retrieval."
    ),
    version="0.3.0",
)


# ==================================================
# REQUEST AND RESPONSE MODELS
# ==================================================

class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    state: Optional[str] = None
    category: Optional[str] = None
    age: Optional[int] = Field(default=None, ge=0, le=120)
    annual_income: Optional[float] = Field(default=None, ge=0)
    education_level: Optional[str] = None
    applicant_category: Optional[str] = None
    top_k: int = Field(default=3, ge=1, le=8)


class Source(BaseModel):
    scheme_id: str = ""
    scheme_name: str
    source_title: str
    source_url: str = ""
    source_pages: list[int] = Field(default_factory=list)
    academic_year: str = "Unknown"
    last_verified: str = "Unknown"
    official: bool = False
    matched_text: str


class AskResponse(BaseModel):
    answer: str
    sources: list[Source]
    mode: str
    disclaimer: str


# ==================================================
# HELPER FUNCTIONS
# ==================================================

def as_text(value: Any) -> str:
    """Convert different data types into readable text."""

    if value is None:
        return ""

    if isinstance(value, list):
        return "; ".join(
            str(item) for item in value if item is not None
        )

    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)

    return str(value)


def get_scheme_name(scheme: dict[str, Any]) -> str:
    """Return the best available scheme/document name."""

    return (
        as_text(scheme.get("name"))
        or as_text(scheme.get("scheme_name"))
        or as_text(scheme.get("title"))
        or "Unnamed scheme/document"
    )


def record_text(scheme: dict[str, Any]) -> str:
    """Convert a scheme record or PDF chunk into searchable text."""

    fields = [
        "name",
        "scheme_name",
        "title",
        "department",
        "state",
        "category",
        "academic_year",
        "summary",
        "text",
        "content",
        "chunk_text",
        "eligibility",
        "documents",
        "application_steps",
        "source_title",
    ]

    parts = []

    for field in fields:
        value = as_text(scheme.get(field)).strip()

        if value:
            parts.append(value)

    return "\n".join(parts)


def get_source_pages(scheme: dict[str, Any]) -> list[int]:
    """Normalize source page metadata."""

    raw_pages = (
        scheme.get("source_pages")
        or scheme.get("pages")
        or scheme.get("page")
        or []
    )

    if not isinstance(raw_pages, list):
        raw_pages = [raw_pages]

    pages = []

    for page in raw_pages:
        try:
            pages.append(int(page))
        except (TypeError, ValueError):
            continue

    return pages


# ==================================================
# LOAD SCHEME DATA
# ==================================================

def load_records(path: Path) -> list[dict[str, Any]]:
    """Load JSON records from a file."""

    if not path.exists():
        print(f"Data file not found: {path}")
        return []

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

    except (json.JSONDecodeError, OSError) as exc:
        print(
            f"Could not load {path}: "
            f"{type(exc).__name__}: {exc}"
        )
        return []

    if isinstance(data, list):
        return [
            item for item in data
            if isinstance(item, dict)
        ]

    if isinstance(data, dict):

        for key in (
            "schemes",
            "chunks",
            "records",
            "documents",
        ):
            items = data.get(key)

            if isinstance(items, list):
                return [
                    item for item in items
                    if isinstance(item, dict)
                ]

        if any(
            key in data
            for key in (
                "name",
                "scheme_name",
                "title",
                "text",
                "content",
            )
        ):
            return [data]

    return []


def load_schemes() -> list[dict[str, Any]]:
    """Load scheme metadata and extracted PDF chunks."""

    records = []

    records.extend(load_records(SCHEMES_PATH))
    records.extend(load_records(CHUNKS_PATH))

    for index, record in enumerate(records):
        record["_record_index"] = index

    print(f"Loaded {len(records)} scheme records and chunks.")

    return records


SCHEMES = load_schemes()


# ==================================================
# LOAD HUGGING FACE EMBEDDING MODEL
# ==================================================

# Load the embedding model only when retrieval is first needed.
# This allows lightweight endpoints such as / and /health to start
# before loading PyTorch and the transformer model.
embedding_model = None


def get_embedding_model():
    """Load the sentence-transformer model on demand."""
    global embedding_model

    if embedding_model is None:
        print(f"Loading embedding model: {EMBEDDING_MODEL_NAME}")
        from sentence_transformers import SentenceTransformer

        embedding_model = SentenceTransformer(
            EMBEDDING_MODEL_NAME,
            device="cpu",
        )

    return embedding_model


# ==================================================
# INITIALIZE PERSISTENT CHROMADB
# ==================================================

CHROMA_PATH.mkdir(
    parents=True,
    exist_ok=True,
)

chroma_client = chromadb.PersistentClient(
    path=str(CHROMA_PATH)
)

collection = chroma_client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={"hnsw:space": "cosine"},
)


# ==================================================
# INDEX SCHEME RECORDS
# ==================================================

def index_schemes() -> None:
    """Create embeddings in small batches and store them in ChromaDB."""

    if collection.count() > 0:
        print(
            f"ChromaDB already contains {collection.count()} records; "
            "skipping re-indexing."
        )
        return

    valid_records = []

    for index, scheme in enumerate(SCHEMES):
        document = record_text(scheme)

        if not document:
            continue

        valid_records.append((
            f"record-{index}",
            document,
            {
                "record_index": index,
                "state": as_text(scheme.get("state")) or "unknown",
                "category": as_text(scheme.get("category")) or "unknown",
                "scheme_name": get_scheme_name(scheme),
            },
        ))

    if not valid_records:
        print(
            "No searchable records found. Check "
            "schemes.json and scheme_chunks.json."
        )
        return

    model = get_embedding_model()
    batch_size = 8

    for start in range(0, len(valid_records), batch_size):
        batch = valid_records[start:start + batch_size]

        batch_ids = [item[0] for item in batch]
        batch_documents = [item[1] for item in batch]
        batch_metadatas = [item[2] for item in batch]

        batch_embeddings = model.encode(
            batch_documents,
            batch_size=4,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        ).tolist()

        collection.upsert(
            ids=batch_ids,
            documents=batch_documents,
            metadatas=batch_metadatas,
            embeddings=batch_embeddings,
        )

        print(
            f"Indexed {min(start + batch_size, len(valid_records))}"
            f"/{len(valid_records)} records."
        )

    print(f"Indexed {len(valid_records)} records in ChromaDB.")


# ==================================================
# SEMANTIC RETRIEVAL
# ==================================================

def retrieve(
    question: str,
    top_k: int,
    state: Optional[str] = None,
    category: Optional[str] = None,
) -> list[tuple[dict[str, Any], float, str]]:
    """Retrieve relevant records using vector similarity."""

    if not SCHEMES:
        return []

    if collection.count() == 0:
        index_schemes()

    if collection.count() == 0:
        return []

    model = get_embedding_model()
    query_embedding = model.encode(
        [question],
        batch_size=1,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    ).tolist()

    result = collection.query(
        query_embeddings=query_embedding,
        n_results=min(top_k, collection.count()),
        include=[
            "documents",
            "metadatas",
            "distances",
        ],
    )

    distances = result.get("distances", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]
    documents = result.get("documents", [[]])[0]

    matches = []

    for distance, metadata, document in zip(
        distances,
        metadatas,
        documents,
    ):

        try:
            index = int(metadata["record_index"])

        except (KeyError, TypeError, ValueError):
            continue

        if index < 0 or index >= len(SCHEMES):
            continue

        scheme = SCHEMES[index]

        # Optional state filter.
        if state and state.strip().lower() not in (
            "any",
            "all",
            "",
        ):
            requested_state = state.strip().lower()

            scheme_state = (
                as_text(scheme.get("state"))
                .strip()
                .lower()
            )

            allowed_states = (
                "central",
                "all india",
                "india",
                requested_state,
                "unknown",
                "",
            )

            if scheme_state not in allowed_states:
                continue

        # Optional category filter.
        if category and category.strip().lower() not in (
            "any",
            "all",
            "",
        ):
            requested_category = category.strip().lower()

            scheme_category = (
                as_text(scheme.get("category"))
                .strip()
                .lower()
            )

            if (
                scheme_category
                and scheme_category != requested_category
            ):
                continue

        # Cosine distance 0 means maximally similar.
        similarity = 1.0 - float(distance)

        matches.append((
            scheme,
            similarity,
            document or "",
        ))

    matches.sort(
        key=lambda item: item[1],
        reverse=True,
    )

    return matches[:top_k]


# ==================================================
# PURE RAG ANSWER
# No Gemini or other generative LLM
# ==================================================

def fallback_answer(
    question: str,
    results: list[tuple[dict[str, Any], float, str]],
) -> str:
    """Return retrieved evidence without generating unsupported claims."""

    if not results:
        return (
            "## No relevant information found\n\n"
            "I could not retrieve a relevant passage from the "
            "current scheme database. This does not prove that "
            "no scheme exists. Try rephrasing your question or "
            "add verified official scheme documents."
        )

    output = [
        "## Retrieved scheme information"
    ]

    for scheme, score, matched_text in results:

        name = get_scheme_name(scheme)

        summary = (
            as_text(scheme.get("summary"))
            or as_text(scheme.get("text"))
            or as_text(scheme.get("content"))
            or matched_text
        )

        output.append(f"### {name}")

        output.append(
            f"**Relevant passage:**\n\n{summary[:2500]}"
        )

        fields = [
            ("eligibility", "Eligibility recorded"),
            ("documents", "Documents recorded"),
            ("application_steps", "Application steps recorded"),
        ]

        for field, label in fields:
            value = as_text(scheme.get(field))

            if value:
                output.append(f"**{label}:** {value}")

        source_title = (
            as_text(scheme.get("source_title"))
            or as_text(scheme.get("source_file"))
            or "Unknown source"
        )

        output.append(f"**Source:** {source_title}")

        pages = get_source_pages(scheme)

        if pages:
            output.append(
                "**Source page(s):** "
                + ", ".join(map(str, pages))
            )

        academic_year = as_text(
            scheme.get("academic_year")
        )

        if academic_year:
            output.append(
                f"**Academic year in record:** {academic_year}"
            )

        source_url = as_text(
            scheme.get("source_url")
        )

        if source_url:
            output.append(
                f"**Source URL:** {source_url}"
            )

        output.append(
            f"**Retrieval similarity:** {score:.3f} "
            "(not an eligibility probability)."
        )

    output.append(
        "### Important\n\n"
        "These retrieved passages are not a confirmed eligibility "
        "decision. Missing fields mean information was not recorded "
        "in the indexed data; they do not mean a requirement does "
        "not exist. Verify current rules and deadlines with the "
        "relevant official government department."
    )

    return "\n\n".join(output)


# ==================================================
# API ENDPOINTS
# ==================================================

@app.get("/")
def root() -> dict[str, str]:
    return {
        "name": "Government Scheme Eligibility Assistant API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "scheme_records": len(SCHEMES),
        "chroma_records": collection.count(),
        "embedding_model": EMBEDDING_MODEL_NAME,
        "embedding_model_loaded": embedding_model is not None,
        "answer_mode": "extractive_rag",
        "llm_required": False,
    }


@app.get("/schemes")
def list_schemes() -> list[dict[str, Any]]:
    """Return available scheme metadata."""

    return [
        {
            "id": as_text(
                scheme.get("id")
                or scheme.get("scheme_id")
            ),
            "name": get_scheme_name(scheme),
            "state": as_text(scheme.get("state")),
            "category": as_text(scheme.get("category")),
            "academic_year": (
                as_text(scheme.get("academic_year"))
                or "Unknown"
            ),
            "official": bool(
                scheme.get("official", False)
            ),
            "source_title": (
                as_text(scheme.get("source_title"))
                or as_text(scheme.get("source_file"))
            ),
            "source_url": as_text(
                scheme.get("source_url")
            ),
            "last_verified": (
                as_text(scheme.get("last_verified"))
                or "Unknown"
            ),
        }
        for scheme in SCHEMES
    ]


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    """Retrieve scheme evidence and return an extractive answer."""

    try:
        results = retrieve(
            question=request.question,
            top_k=request.top_k,
            state=request.state,
            category=request.category,
        )

    except Exception as exc:
        print(
            f"Retrieval failed: {type(exc).__name__}: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Scheme retrieval failed. "
                "Check the API terminal logs."
            ),
        ) from exc

    answer = fallback_answer(
        request.question,
        results,
    )

    sources = []

    for scheme, score, matched_text in results:

        sources.append(
            Source(
                scheme_id=as_text(
                    scheme.get("id")
                    or scheme.get("scheme_id")
                ),
                scheme_name=get_scheme_name(scheme),
                source_title=(
                    as_text(scheme.get("source_title"))
                    or as_text(scheme.get("source_file"))
                    or "Unknown source"
                ),
                source_url=as_text(
                    scheme.get("source_url")
                ),
                source_pages=get_source_pages(scheme),
                academic_year=(
                    as_text(scheme.get("academic_year"))
                    or "Unknown"
                ),
                last_verified=(
                    as_text(scheme.get("last_verified"))
                    or "Unknown"
                ),
                official=bool(
                    scheme.get("official", False)
                ),
                matched_text=matched_text[:700],
            )
        )

    return AskResponse(
        answer=answer,
        sources=sources,
        mode="extractive_rag",
        disclaimer=DISCLAIMER,
    )


