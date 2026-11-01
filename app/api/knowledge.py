import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.config import settings
from app.database.connection import get_db
from app.database.models import Document
from app.rag.ingestion import ingest_document
from app.rag.service import answer_question


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/knowledge",
    tags=["Knowledge Base"]
)


class QuestionRequest(BaseModel):

    question: str = Field(
        min_length=3,
        max_length=2000
    )

    top_k: int = Field(
        default=4,
        ge=1,
        le=10
    )


@router.post("/documents")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required."
        )

    content = await file.read()

    max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    if len(content) > max_size:
        raise HTTPException(
            status_code=413,
            detail=f"Maximum upload size is {settings.MAX_UPLOAD_SIZE_MB} MB."
        )

    try:

        document, created = ingest_document(
            db=db,
            filename=file.filename,
            file_bytes=content
        )

        return {
            "message": (
                "Document uploaded and indexed successfully."
                if created else
                "This document has already been indexed."
            ),
            "created": created,
            "document_id": document.id,
            "filename": document.filename,
            "chunk_count": document.chunk_count
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except Exception as exc:

        logger.exception("Document ingestion failed")

        raise HTTPException(
            status_code=500,
            detail="Document ingestion failed. Check the server logs."
        ) from exc


@router.get("/documents")
def list_documents(
    db: Session = Depends(get_db)
):

    documents = (
        db.query(Document)
        .order_by(Document.created_at.desc())
        .all()
    )

    return [
        {
            "id": document.id,
            "filename": document.filename,
            "file_type": document.file_type,
            "chunk_count": document.chunk_count,
            "created_at": document.created_at
        }
        for document in documents
    ]


@router.post("/query")
async def query_knowledge_base(
    request: QuestionRequest,
    db: Session = Depends(get_db)
):

    try:

        return await answer_question(
            db=db,
            question=request.question,
            top_k=request.top_k
        )

    except Exception as exc:

        logger.exception("Knowledge base query failed")

        raise HTTPException(
            status_code=500,
            detail="Knowledge base query failed. Check the server logs."
        ) from exc