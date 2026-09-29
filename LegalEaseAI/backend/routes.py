from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from backend.schemas import DocumentRequest
from backend.services.document_service import extract_terms
from backend.services.exporters import (
    filename_for,
    make_docx,
    make_pdf,
    make_txt,
)


router = APIRouter()


# ============================================================
# ROOT
# ============================================================

@router.get("/")
def root():
    return {
        "message": "LegalEase API is running"
    }


# ============================================================
# HEALTH
# ============================================================

@router.get("/health")
def health():
    return {
        "status": "healthy"
    }


# ============================================================
# GENERATE DOCUMENT
# ============================================================

@router.post("/generate")
def generate_document(request: DocumentRequest):

    try:
        from ai_core.gemini_generator import (
            GeminiLegalGenerator,
        )

        generator = GeminiLegalGenerator()

        content = generator.generate(
            document_type=request.document_type,
            parties=request.parties,
            terms=request.terms,
            dates=request.dates,
        )

        terms_list = extract_terms(
            request.terms
        )

        return {
            "document_type": request.document_type,
            "content": content,
            "terms": terms_list,
            "generated_by": generator.generated_by,
        }

    except Exception as exc:

        print("\n" + "=" * 70)
        print("GENERATE ERROR")
        print("=" * 70)
        print(repr(exc))
        print("=" * 70 + "\n")

        raise HTTPException(
            status_code=500,
            detail=f"Document generation failed: {exc}",
        )


# ============================================================
# TXT EXPORT
# ============================================================

@router.post("/export/txt")
def export_txt(request: dict):

    try:

        document_type = str(
            request.get(
                "document_type",
                "Legal Document",
            )
        )

        content = str(
            request.get(
                "content",
                "",
            )
        ).strip()

        if not content:
            raise HTTPException(
                status_code=400,
                detail="Document content is required.",
            )

        file = make_txt(content)

        return Response(
            content=file.getvalue(),
            media_type="text/plain; charset=utf-8",
            headers={
                "Content-Disposition": (
                    "attachment; "
                    f'filename="{filename_for(document_type, "txt")}"'
                )
            },
        )

    except HTTPException:
        raise

    except Exception as exc:

        print("\n" + "=" * 70)
        print("TXT EXPORT ERROR")
        print("=" * 70)
        print(repr(exc))
        print("=" * 70 + "\n")

        raise HTTPException(
            status_code=500,
            detail=f"TXT export failed: {exc}",
        )


# ============================================================
# DOCX EXPORT
# ============================================================

@router.post("/export/docx")
def export_docx(request: dict):

    try:

        document_type = str(
            request.get(
                "document_type",
                "Legal Document",
            )
        )

        content = str(
            request.get(
                "content",
                "",
            )
        ).strip()

        terms = request.get(
            "terms",
            [],
        )

        if not isinstance(terms, list):
            terms = []

        terms = [
            str(term)
            for term in terms
            if str(term).strip()
        ]

        if not content:
            raise HTTPException(
                status_code=400,
                detail="Document content is required.",
            )

        file = make_docx(
            document_type=document_type,
            content=content,
            terms=terms,
        )

        return Response(
            content=file.getvalue(),
            media_type=(
                "application/vnd.openxmlformats-"
                "officedocument.wordprocessingml.document"
            ),
            headers={
                "Content-Disposition": (
                    "attachment; "
                    f'filename="{filename_for(document_type, "docx")}"'
                )
            },
        )

    except HTTPException:
        raise

    except Exception as exc:

        print("\n" + "=" * 70)
        print("DOCX EXPORT ERROR")
        print("=" * 70)
        print(repr(exc))
        print("=" * 70 + "\n")

        raise HTTPException(
            status_code=500,
            detail=f"DOCX export failed: {exc}",
        )


# ============================================================
# PDF EXPORT
# ============================================================

@router.post("/export/pdf")
def export_pdf(request: dict):

    try:

        print("\n" + "=" * 70)
        print("PDF EXPORT REQUEST")
        print("=" * 70)

        print(
            "REQUEST TYPE:",
            type(request),
        )

        print(
            "REQUEST:",
            repr(request),
        )

        # ----------------------------------------------------
        # Document type
        # ----------------------------------------------------

        document_type = str(
            request.get(
                "document_type",
                "Legal Document",
            )
        ).strip()

        if not document_type:
            document_type = "Legal Document"

        print(
            "DOCUMENT TYPE:",
            repr(document_type),
        )

        # ----------------------------------------------------
        # Document content
        # ----------------------------------------------------

        content = str(
            request.get(
                "content",
                "",
            )
        ).strip()

        print(
            "CONTENT LENGTH:",
            len(content),
        )

        if not content:

            raise HTTPException(
                status_code=400,
                detail="Document content is required.",
            )

        # ----------------------------------------------------
        # Terms
        # ----------------------------------------------------

        terms = request.get(
            "terms",
            [],
        )

        print(
            "TERMS TYPE:",
            type(terms),
        )

        print(
            "TERMS:",
            repr(terms),
        )

        if not isinstance(terms, list):
            terms = []

        terms = [
            str(term)
            for term in terms
            if str(term).strip()
        ]

        print(
            "CLEAN TERMS:",
            repr(terms),
        )

        # ----------------------------------------------------
        # Generate PDF
        # ----------------------------------------------------

        print(
            "Calling make_pdf()..."
        )

        file = make_pdf(
            document_type=document_type,
            content=content,
        )

        print(
            "make_pdf() completed."
        )

        # ----------------------------------------------------
        # Read PDF bytes
        # ----------------------------------------------------

        pdf_data = file.getvalue()

        print(
            "PDF SIZE:",
            len(pdf_data),
        )

        if not pdf_data:

            raise RuntimeError(
                "PDF generator returned empty data."
            )

        # ----------------------------------------------------
        # Return PDF
        # ----------------------------------------------------

        filename = filename_for(
            document_type,
            "pdf",
        )

        print(
            "FILENAME:",
            filename,
        )

        print(
            "Returning PDF response..."
        )

        response = Response(
            content=pdf_data,
            media_type="application/pdf",
            headers={
                "Content-Disposition": (
                    "attachment; "
                    f'filename="{filename}"'
                )
            },
        )

        print(
            "PDF RESPONSE CREATED SUCCESSFULLY."
        )

        print("=" * 70 + "\n")

        return response

    except HTTPException:
        raise

    except Exception as exc:

        import traceback

        print("\n" + "=" * 70)
        print("PDF EXPORT ERROR")
        print("=" * 70)

        print(
            "EXCEPTION TYPE:",
            type(exc).__name__,
        )

        print(
            "EXCEPTION:",
            repr(exc),
        )

        print("\nTRACEBACK:")

        traceback.print_exc()

        print("=" * 70 + "\n")

        raise HTTPException(
            status_code=500,
            detail=(
                "PDF export failed: "
                f"{type(exc).__name__}: {exc}"
            ),
        )