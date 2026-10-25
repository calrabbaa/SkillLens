from io import BytesIO

from pypdf import PdfReader
from pypdf.errors import PdfReadError


MAX_PDF_PAGES = 4
MAX_EXTRACTED_CHARS = 20_000


def extract_pdf_text(file_bytes: bytes) -> str:
    """
    Extract text from a CV while enforcing
    page-count and text-length limits.
    """

    try:
        reader = PdfReader(BytesIO(file_bytes))
    except (PdfReadError, OSError, ValueError) as exc:
        raise ValueError(
            "The uploaded file is not a readable PDF."
        ) from exc

    if reader.is_encrypted:
        raise ValueError(
            "Password-protected PDFs are not supported."
        )

    if len(reader.pages) > MAX_PDF_PAGES:
        raise ValueError(
            f"The CV must contain at most {MAX_PDF_PAGES} pages."
        )

    text_parts = []
    total_chars = 0

    for page in reader.pages:
        try:
            text = page.extract_text()
        except (PdfReadError, ValueError) as exc:
            raise ValueError(
                "Could not extract text from the PDF."
            ) from exc

        if text:
            total_chars += len(text)

            if total_chars > MAX_EXTRACTED_CHARS:
                raise ValueError(
                    "The CV contains too much text. "
                    "Maximum: 20,000 characters."
                )

            text_parts.append(text)

    extracted_text = "\n".join(text_parts).strip()

    if not extracted_text:
        raise ValueError(
            "No extractable text was found in the PDF."
        )

    return extracted_text
