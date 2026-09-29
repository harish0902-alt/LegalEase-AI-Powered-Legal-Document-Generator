from backend.services.exporters import (
    make_docx,
    make_pdf,
    make_txt,
)


def test_txt_export():

    file = make_txt(
        "LegalEase test document."
    )

    assert file.getvalue() == (
        b"LegalEase test document."
    )


def test_docx_export():

    file = make_docx(
        document_type="Agreement",
        content="Test legal document.",
        terms=["Payment", "Confidentiality"],
    )

    assert file.getvalue().startswith(
        b"PK"
    )


def test_pdf_export():

    file = make_pdf(
        document_type="Agreement",
        content="Test legal document.",
    )

    assert file.getvalue().startswith(
        b"%PDF"
    )