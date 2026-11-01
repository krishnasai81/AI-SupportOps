from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.config import settings


QUERY_PREFIX = (
    "Represent this sentence for searching relevant passages: "
)


@lru_cache(maxsize=1)
def get_embedding_model():

    return SentenceTransformer(
        settings.EMBEDDING_MODEL,
        device="cpu"
    )


def generate_embeddings(texts: list[str]) -> list[list[float]]:

    if not texts:
        return []

    model = get_embedding_model()

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False
    )

    return embeddings.tolist()


def generate_query_embedding(query: str) -> list[float]:

    query_text = QUERY_PREFIX + query

    return generate_embeddings([query_text])[0]