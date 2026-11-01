from app.config import settings


def split_text(
    text: str,
    chunk_size: int | None = None,
    overlap: int | None = None
) -> list[str]:

    chunk_size = chunk_size or settings.CHUNK_SIZE
    overlap = (
        settings.CHUNK_OVERLAP if overlap is None else overlap
    )

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "overlap must be >= 0 and smaller than chunk_size"
        )

    text = " ".join(text.split())

    if not text:
        return []

    chunks = []
    start = 0
    step = chunk_size - overlap

    while start < len(text):

        end = min(start + chunk_size, len(text))

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end == len(text):
            break

        start += step

    return chunks