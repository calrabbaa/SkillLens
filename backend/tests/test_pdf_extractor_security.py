from types import SimpleNamespace

import pytest

from services import pdf_extractor


def mock_pdf(page_texts, encrypted=False):
    """Create a fake PDF reader without needing PDF files."""
    pages = [
        SimpleNamespace(
            extract_text=lambda text=text: text
        )
        for text in page_texts
    ]

    return SimpleNamespace(
        is_encrypted=encrypted,
        pages=pages,
    )


def test_accepts_four_pages(monkeypatch):
    monkeypatch.setattr(
        pdf_extractor,
        "PdfReader",
        lambda _: mock_pdf(["Python developer"] * 4),
    )

    result = pdf_extractor.extract_pdf_text(b"test")

    assert result.count("Python developer") == 4


def test_rejects_more_than_four_pages(monkeypatch):
    monkeypatch.setattr(
        pdf_extractor,
        "PdfReader",
        lambda _: mock_pdf(["Python developer"] * 5),
    )

    with pytest.raises(ValueError, match="at most 4 pages"):
        pdf_extractor.extract_pdf_text(b"test")


def test_rejects_excessive_text(monkeypatch):
    monkeypatch.setattr(
        pdf_extractor,
        "PdfReader",
        lambda _: mock_pdf(["A" * 20_001]),
    )

    with pytest.raises(ValueError, match="too much text"):
        pdf_extractor.extract_pdf_text(b"test")


def test_rejects_encrypted_pdf(monkeypatch):
    monkeypatch.setattr(
        pdf_extractor,
        "PdfReader",
        lambda _: mock_pdf(["Python"], encrypted=True),
    )

    with pytest.raises(ValueError, match="Password-protected"):
        pdf_extractor.extract_pdf_text(b"test")


def test_rejects_empty_pdf(monkeypatch):
    monkeypatch.setattr(
        pdf_extractor,
        "PdfReader",
        lambda _: mock_pdf([""]),
    )

    with pytest.raises(ValueError, match="No extractable text"):
        pdf_extractor.extract_pdf_text(b"test")
