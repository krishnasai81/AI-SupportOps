import pytest

from app.rag.chunking import split_text
from app.rag.document_loader import extract_text


def test_chunking_creates_multiple_chunks():

    text = "A" * 2000

    chunks = split_text(
        text,
        chunk_size=500,
        overlap=100
    )

    assert len(chunks) > 1
    assert all(len(chunk) <= 500 for chunk in chunks)


def test_chunking_preserves_overlap():

    text = "A" * 1000

    chunks = split_text(
        text,
        chunk_size=300,
        overlap=50
    )

    assert chunks[0][-50:] == chunks[1][:50]


def test_empty_text_returns_empty_list():

    assert split_text("   ") == []


def test_invalid_overlap_raises_error():

    with pytest.raises(ValueError):
        split_text(
            "Some text",
            chunk_size=100,
            overlap=100
        )


def test_txt_document_extraction():

    content = b"CloudDesk provides customer support."

    result = extract_text(
        "knowledge.txt",
        content
    )

    assert "CloudDesk" in result


def test_unsupported_document_format():

    with pytest.raises(ValueError):
        extract_text(
            "document.exe",
            b"some content"
        )