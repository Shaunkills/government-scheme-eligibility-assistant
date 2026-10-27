
import json
import re
from pathlib import Path
from typing import Any

from pypdf import PdfReader


# --------------------------------------------------
# Configuration
# --------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent

RAW_DIR = ROOT / "data" / "raw"
OUTPUT_PATH = ROOT / "data" / "processed" / "scheme_chunks.json"

CHUNK_SIZE = 900
OVERLAP = 150

# This PDF's published guidelines say they apply to 2025-26.
DEFAULT_ACADEMIC_YEAR = "2025-26"


# --------------------------------------------------
# Text cleaning
# --------------------------------------------------

def clean_text(text: str) -> str:
    """Normalize whitespace while preserving readable text."""
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# --------------------------------------------------
# Chunking
# --------------------------------------------------

def split_into_chunks(text: str) -> list[str]:
    """Split text into overlapping character-based chunks."""
    text = clean_text(text)

    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        # Repeat the last OVERLAP characters in the next chunk.
        start = max(end - OVERLAP, start + 1)

    return chunks


# --------------------------------------------------
# Source metadata
# --------------------------------------------------

def get_academic_year(pdf_path: Path) -> str:
    """
    Use the year stated in the document where identifiable.
    The known Top Class SC Scholarship PDF is applicable from 2025-26.
    """
    filename = pdf_path.name.lower()

    if "top_class_sc_students_2026_27" in filename:
        # The filename alone does not establish the policy year.
        return DEFAULT_ACADEMIC_YEAR

    return DEFAULT_ACADEMIC_YEAR


def extract_pdf(pdf_path: Path) -> list[dict[str, Any]]:
    """Extract text page by page and generate metadata-rich chunks."""
    print(f"Reading PDF: {pdf_path.name}")

    reader = PdfReader(str(pdf_path))
    records = []

    academic_year = get_academic_year(pdf_path)

    for page_number, page in enumerate(reader.pages, start=1):
        try:
            page_text = page.extract_text() or ""
        except Exception as exc:
            print(
                f"Skipping unreadable page {page_number}: "
                f"{type(exc).__name__}"
            )
            continue

        page_text = clean_text(page_text)

        if not page_text:
            print(f"No extractable text on page {page_number}.")
            continue

        chunks = split_into_chunks(page_text)

        for chunk_number, chunk in enumerate(chunks, start=1):
            records.append({
                "id": (
                    f"{pdf_path.stem}-page-{page_number}"
                    f"-chunk-{chunk_number}"
                ),
                "name": pdf_path.stem.replace("_", " "),
                "department": "Government of India",
                "state": "Central",
                "category": "SC",
                "academic_year": academic_year,
                "summary": chunk,
                "eligibility": [],
                "documents": [],
                "application_steps": [],
                "source_title": pdf_path.name,
                "source_url": "",
                "source_pages": [page_number],
                "official": False,
                "last_verified": "Not independently verified",
            })

    print(f"Extracted {len(records)} chunks from {pdf_path.name}")
    return records


# --------------------------------------------------
# Main ingestion process
# --------------------------------------------------

def main() -> None:
    if not RAW_DIR.exists():
        raise FileNotFoundError(
            f"PDF input folder does not exist: {RAW_DIR}"
        )

    pdf_files = sorted(RAW_DIR.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError(
            f"No PDF files found in {RAW_DIR}. "
            "Place your scheme PDFs in data/raw/."
        )

    all_records = []

    for pdf_path in pdf_files:
        all_records.extend(extract_pdf(pdf_path))

    if not all_records:
        raise RuntimeError(
            "No text chunks were extracted. "
            "The PDFs may be scanned images requiring OCR."
        )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_PATH.open("w", encoding="utf-8") as file:
        json.dump(
            all_records,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print("\nIngestion completed successfully.")
    print(f"PDF files processed: {len(pdf_files)}")
    print(f"Total chunks: {len(all_records)}")
    print(f"Output: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
