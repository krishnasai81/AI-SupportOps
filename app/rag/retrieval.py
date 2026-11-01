
import math
import re

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.models import Document, DocumentChunk
from app.rag.embeddings import generate_query_embedding


def cosine_similarity(
    a: list[float],
    b: list[float]
) -> float:

    dot = sum(x * y for x, y in zip(a, b))

    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)


def reciprocal_rank_fusion(
    semantic_results: list[dict],
    keyword_results: list[dict],
    top_k: int,
    constant: int = 60
) -> list[dict]:

    combined = {}

    for rank, item in enumerate(semantic_results, start=1):

        chunk_id = item["chunk_id"]

        combined[chunk_id] = {
            **item,
            "hybrid_score": 1.0 / (constant + rank)
        }

    for rank, item in enumerate(keyword_results, start=1):

        chunk_id = item["chunk_id"]

        if chunk_id in combined:

            combined[chunk_id]["hybrid_score"] += (
                1.0 / (constant + rank)
            )

        else:

            combined[chunk_id] = {
                **item,
                "hybrid_score": 1.0 / (constant + rank)
            }

    results = list(combined.values())

    results.sort(
        key=lambda item: item["hybrid_score"],
        reverse=True
    )

    return results[:top_k]


def retrieve_relevant_chunks(
    db: Session,
    query: str,
    top_k: int = 4
) -> list[dict]:

    if not query or not query.strip():
        return []

    if top_k < 1:
        return []

    query_embedding = generate_query_embedding(query)

    dialect = db.get_bind().dialect.name

    # --------------------------------------------------------
    # POSTGRESQL HYBRID SEARCH
    # --------------------------------------------------------

    if dialect == "postgresql":

        embedding_string = (
            "[" + ",".join(
                str(float(value))
                for value in query_embedding
            ) + "]"
        )

        semantic_sql = text("""
            SELECT
                dc.id AS chunk_id,
                dc.document_id,
                dc.chunk_index,
                dc.content,
                d.filename,
                1.0 - (
                    dc.embedding <=> CAST(:embedding AS vector)
                ) AS similarity

            FROM document_chunks AS dc

            JOIN documents AS d
                ON d.id = dc.document_id

            ORDER BY dc.embedding <=> CAST(:embedding AS vector)

            LIMIT :top_k
        """)

        keyword_sql = text("""
            SELECT
                dc.id AS chunk_id,
                dc.document_id,
                dc.chunk_index,
                dc.content,
                d.filename,
                0.0::double precision AS similarity,

                ts_rank_cd(
                    to_tsvector('english', dc.content),
                    plainto_tsquery('english', :query)
                ) AS keyword_score

            FROM document_chunks AS dc

            JOIN documents AS d
                ON d.id = dc.document_id

            WHERE to_tsvector('english', dc.content)
                @@ plainto_tsquery('english', :query)

            ORDER BY keyword_score DESC

            LIMIT :top_k
        """)

        semantic_rows = db.execute(
            semantic_sql,
            {
                "embedding": embedding_string,
                "top_k": top_k
            }
        ).mappings().all()

        keyword_rows = db.execute(
            keyword_sql,
            {
                "query": query,
                "top_k": top_k
            }
        ).mappings().all()

        semantic_results = [
            dict(row)
            for row in semantic_rows
        ]

        keyword_results = [
            dict(row)
            for row in keyword_rows
        ]

        return reciprocal_rank_fusion(
            semantic_results,
            keyword_results,
            top_k
        )

    # --------------------------------------------------------
    # SQLITE FALLBACK FOR TESTING
    # --------------------------------------------------------

    records = (
        db.query(DocumentChunk, Document)
        .join(
            Document,
            Document.id == DocumentChunk.document_id
        )
        .all()
    )

    semantic_results = []
    keyword_results = []

    query_words = set(
        re.findall(r"\w+", query.lower())
    )

    for chunk, document in records:

        similarity = cosine_similarity(
            query_embedding,
            chunk.embedding
        )

        item = {
            "chunk_id": chunk.id,
            "document_id": document.id,
            "filename": document.filename,
            "chunk_index": chunk.chunk_index,
            "content": chunk.content,
            "similarity": round(similarity, 4)
        }

        semantic_results.append(item)

        content_words = set(
            re.findall(r"\w+", chunk.content.lower())
        )

        matches = len(
            query_words.intersection(content_words)
        )

        if matches:

            keyword_results.append({
                **item,
                "keyword_score": matches
            })

    semantic_results.sort(
        key=lambda item: item["similarity"],
        reverse=True
    )

    keyword_results.sort(
        key=lambda item: item["keyword_score"],
        reverse=True
    )

    return reciprocal_rank_fusion(
        semantic_results[:top_k],
        keyword_results[:top_k],
        top_k
    )
