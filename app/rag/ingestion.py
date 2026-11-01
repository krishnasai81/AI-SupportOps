import hashlib

from sqlalchemy.orm import Session

from app.database.models import Document, DocumentChunk
from app.rag.document_loader import extract_text
from app.rag.chunking import split_text
from app.rag.embeddings import generate_embeddings


def ingest_document(
    db: Session,
    filename: str,
    file_bytes: bytes
):

    filename = filename.replace("\\", "/").split("/")[-1]

    file_hash = hashlib.sha256(file_bytes).hexdigest()

    existing = (
        db.query(Document)
        .filter(Document.file_hash == file_hash)
        .first()
    )

    if existing:
        return existing, False

    text = extract_text(filename, file_bytes)

    chunks = split_text(text)

    if not chunks:
        raise ValueError("Document contains no usable text.")

    embeddings = generate_embeddings(chunks)

    extension = filename.rsplit(".", 1)[-1].lower()

    document = Document(
        filename=filename,
        file_type=extension,
        file_hash=file_hash,
        chunk_count=len(chunks)
    )

    try:

        db.add(document)
        db.flush()

        chunk_records = []

        for index, (content, embedding) in enumerate(
            zip(chunks, embeddings)
        ):

            chunk_records.append(
                DocumentChunk(
                    document_id=document.id,
                    chunk_index=index,
                    content=content,
                    embedding=embedding
                )
            )

        db.add_all(chunk_records)

        db.commit()
        db.refresh(document)

        return document, True

    except Exception:

        db.rollback()
        raise