from io import BytesIO

from pypdf import PdfReader


def extract_pdf_text(file_bytes: bytes) -> str:
    """
    Extract text from all pages of a PDF.
    """

    reader = PdfReader(BytesIO(file_bytes))

    text_parts = []

    for page in reader.pages:
        text = page.extract_text()

        if text:
            text_parts.append(text)

    extracted_text = "\n".join(text_parts).strip()

    if not extracted_text:
        raise ValueError(
            "No extractable text was found in the PDF."
        )

    return extracted_text
