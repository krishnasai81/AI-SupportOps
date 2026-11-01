from io import BytesIO
from pathlib import Path

from pypdf import PdfReader


SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".txt",
    ".md",
    ".markdown"
}


def extract_text(filename: str, file_bytes: bytes) -> str:

    extension = Path(filename).suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            "Unsupported file format. Upload PDF, TXT or Markdown."
        )

    if extension == ".pdf":

        reader = PdfReader(BytesIO(file_bytes))

        if reader.is_encrypted:
            raise ValueError(
                "Password-protected PDFs are not supported."
            )

        pages = []

        for page in reader.pages:
            page_text = page.extract_text() or ""

            if page_text.strip():
                pages.append(page_text)

        text = "\n".join(pages)

    else:

        try:
            text = file_bytes.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise ValueError(
                "The text file must use UTF-8 encoding."
            ) from exc

    if not text.strip():
        raise ValueError(
            "No readable text was found in the uploaded document."
        )

    return text