import os
from pathlib import Path

import requests
import streamlit as st
from dotenv import load_dotenv


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

load_dotenv(PROJECT_ROOT / ".env")


BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000",
).rstrip("/")


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 0;
    }

    .subtitle {
        font-size: 18px;
        color: #666;
        margin-top: 0;
        margin-bottom: 25px;
    }

    .section-title {
        font-size: 24px;
        font-weight: 600;
        margin-top: 15px;
        margin-bottom: 10px;
    }

    .status-box {
        padding: 12px;
        border-radius: 8px;
        margin-top: 10px;
        margin-bottom: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# INITIALIZE SESSION STATE
# ============================================================

if "document" not in st.session_state:
    st.session_state.document = ""

if "document_type" not in st.session_state:
    st.session_state.document_type = "Service Agreement"

if "terms" not in st.session_state:
    st.session_state.terms = []


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">⚖️ LegalEase</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    "AI-powered legal document drafting assistant"
    "</div>",
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("Document Details")

    document_type = st.selectbox(
        "Document Type",
        [
            "Service Agreement",
            "Employment Agreement",
            "Rental Agreement",
            "Non-Disclosure Agreement",
            "Partnership Agreement",
            "Freelance Agreement",
            "Consulting Agreement",
            "Sale Agreement",
            "Legal Notice",
            "Custom Legal Document",
        ],
        index=0,
    )

    parties = st.text_area(
        "Parties",
        placeholder=(
            "Example:\n"
            "Party 1: Example Company Pvt. Ltd.\n"
            "Party 2: Example Client"
        ),
        height=130,
    )

    terms = st.text_area(
        "Terms",
        placeholder=(
            "Example:\n"
            "Services to be provided\n"
            "Payment terms\n"
            "Confidentiality\n"
            "Termination"
        ),
        height=180,
    )

    dates = st.text_area(
        "Dates",
        placeholder=(
            "Example:\n"
            "Start date: 1 January 2026\n"
            "End date: 31 December 2026"
        ),
        height=100,
    )

    generate_button = st.button(
        "Generate Document",
        type="primary",
        use_container_width=True,
    )


# ============================================================
# GENERATE DOCUMENT
# ============================================================

if generate_button:

    if not parties.strip():
        st.error("Please enter the parties.")

    elif not terms.strip():
        st.error("Please enter the terms.")

    elif not dates.strip():
        st.error("Please enter the dates.")

    else:

        generate_payload = {
            "document_type": document_type,
            "parties": parties,
            "terms": terms,
            "dates": dates,
        }

        with st.spinner(
            "Generating your legal document..."
        ):

            try:

                generate_response = requests.post(
                    f"{BACKEND_URL}/generate",
                    json=generate_payload,
                    timeout=120,
                )

                if generate_response.status_code == 200:

                    data = generate_response.json()

                    st.session_state.document = (
                        data.get("content", "")
                    )

                    st.session_state.document_type = (
                        data.get(
                            "document_type",
                            document_type,
                        )
                    )

                    st.session_state.terms = data.get(
                        "terms",
                        [],
                    )

                    st.success(
                        "Document generated successfully."
                    )

                else:

                    st.error(
                        "Document generation failed."
                    )

                    st.write(
                        "Backend status:",
                        generate_response.status_code,
                    )

                    st.code(
                        generate_response.text
                    )

            except requests.exceptions.ConnectionError:

                st.error(
                    "Could not connect to the FastAPI backend."
                )

                st.info(
                    "Make sure FastAPI is running on "
                    f"{BACKEND_URL}"
                )

            except requests.exceptions.Timeout:

                st.error(
                    "The backend request timed out."
                )

            except Exception as exc:

                st.error(
                    f"Unexpected error: {exc}"
                )


# ============================================================
# DOCUMENT EDITOR
# ============================================================

st.markdown(
    '<div class="section-title">'
    "Document Preview"
    "</div>",
    unsafe_allow_html=True,
)


if st.session_state.document:

    edited_document = st.text_area(
        "Edit your document before exporting",
        value=st.session_state.document,
        height=550,
        key="document_editor",
    )

    st.session_state.document = edited_document

else:

    st.info(
        "Fill in the document details in the sidebar "
        "and click Generate Document."
    )


# ============================================================
# EXPORT SECTION
# ============================================================

if st.session_state.document:

    st.markdown(
        '<div class="section-title">'
        "Export Document"
        "</div>",
        unsafe_allow_html=True,
    )

    export_payload = {
        "document_type": str(
            st.session_state.document_type
        ),
        "content": str(
            st.session_state.document
        ),
        "terms": list(
            st.session_state.terms
        ),
    }

    col1, col2, col3 = st.columns(3)


    # ========================================================
    # TXT EXPORT
    # ========================================================

    with col1:

        if st.button(
            "Generate TXT",
            use_container_width=True,
            key="generate_txt",
        ):

            try:

                txt_response = requests.post(
                    f"{BACKEND_URL}/export/txt",
                    json=export_payload,
                    timeout=60,
                )

                if txt_response.status_code == 200:

                    st.download_button(
                        label="Download TXT",
                        data=txt_response.content,
                        file_name=(
                            "LegalEase_Document.txt"
                        ),
                        mime="text/plain",
                        use_container_width=True,
                        key="download_txt",
                    )

                    st.success(
                        "TXT generated successfully."
                    )

                else:

                    st.error(
                        "TXT export failed."
                    )

                    st.write(
                        "Backend status:",
                        txt_response.status_code,
                    )

                    st.code(
                        txt_response.text
                    )

            except Exception as exc:

                st.error(
                    f"TXT export error: {exc}"
                )


    # ========================================================
    # DOCX EXPORT
    # ========================================================

    with col2:

        if st.button(
            "Generate DOCX",
            use_container_width=True,
            key="generate_docx",
        ):

            try:

                docx_response = requests.post(
                    f"{BACKEND_URL}/export/docx",
                    json=export_payload,
                    timeout=60,
                )

                if docx_response.status_code == 200:

                    st.download_button(
                        label="Download DOCX",
                        data=docx_response.content,
                        file_name=(
                            "LegalEase_Document.docx"
                        ),
                        mime=(
                            "application/vnd.openxmlformats-"
                            "officedocument.wordprocessingml.document"
                        ),
                        use_container_width=True,
                        key="download_docx",
                    )

                    st.success(
                        "DOCX generated successfully."
                    )

                else:

                    st.error(
                        "DOCX export failed."
                    )

                    st.write(
                        "Backend status:",
                        docx_response.status_code,
                    )

                    st.code(
                        docx_response.text
                    )

            except Exception as exc:

                st.error(
                    f"DOCX export error: {exc}"
                )


    # ========================================================
    # PDF EXPORT
    # ========================================================

    with col3:

        if st.button(
            "Generate PDF",
            use_container_width=True,
            key="generate_pdf",
        ):

            try:

                # --------------------------------------------
                # Send request to FastAPI
                # --------------------------------------------

                pdf_response = requests.post(
                    f"{BACKEND_URL}/export/pdf",
                    json=export_payload,
                    timeout=60,
                )


                # --------------------------------------------
                # Display debugging information
                # --------------------------------------------

                st.write(
                    "Backend status:",
                    pdf_response.status_code,
                )

                st.write(
                    "Content type:",
                    pdf_response.headers.get(
                        "content-type",
                        "Unknown",
                    ),
                )

                st.write(
                    "PDF size:",
                    len(pdf_response.content),
                    "bytes",
                )


                # --------------------------------------------
                # SUCCESS: HTTP 200
                # --------------------------------------------

                if pdf_response.status_code == 200:

                    content_type = (
                        pdf_response.headers.get(
                            "content-type",
                            "",
                        ).lower()
                    )

                    if (
                        "application/pdf"
                        in content_type
                    ):

                        st.success(
                            "PDF generated successfully."
                        )

                        st.download_button(
                            label="Download PDF",
                            data=pdf_response.content,
                            file_name=(
                                "LegalEase_Document.pdf"
                            ),
                            mime="application/pdf",
                            use_container_width=True,
                            key="download_pdf",
                        )

                    else:

                        st.error(
                            "Backend returned HTTP 200, "
                            "but the response is not a PDF."
                        )

                        st.write(
                            "Received content type:",
                            content_type,
                        )

                        st.code(
                            pdf_response.text[:1000]
                        )


                # --------------------------------------------
                # SERVER ERROR: HTTP 500
                # --------------------------------------------

                elif pdf_response.status_code == 500:

                    st.error(
                        "FastAPI returned HTTP 500 "
                        "Internal Server Error."
                    )

                    st.write(
                        "Backend response:"
                    )

                    st.code(
                        pdf_response.text
                    )


                # --------------------------------------------
                # OTHER HTTP ERROR
                # --------------------------------------------

                else:

                    st.error(
                        "PDF export failed."
                    )

                    st.write(
                        "HTTP status:",
                        pdf_response.status_code,
                    )

                    st.code(
                        pdf_response.text
                    )


            # -----------------------------------------------
            # CONNECTION ERROR
            # -----------------------------------------------

            except requests.exceptions.ConnectionError:

                st.error(
                    "Could not connect to the FastAPI backend."
                )

                st.info(
                    f"Backend URL: {BACKEND_URL}"
                )

                st.info(
                    "Make sure FastAPI is running with:"
                )

                st.code(
                    "uvicorn backend.main:app "
                    "--reload "
                    "--host 127.0.0.1 "
                    "--port 8000"
                )


            # -----------------------------------------------
            # TIMEOUT ERROR
            # -----------------------------------------------

            except requests.exceptions.Timeout:

                st.error(
                    "PDF request timed out."
                )


            # -----------------------------------------------
            # INVALID RESPONSE
            # -----------------------------------------------

            except requests.exceptions.RequestException as exc:

                st.error(
                    "Request error while generating PDF."
                )

                st.code(
                    str(exc)
                )


            # -----------------------------------------------
            # ANY OTHER ERROR
            # -----------------------------------------------

            except Exception as exc:

                st.error(
                    "Unexpected PDF error."
                )

                st.code(
                    str(exc)
                )


# ============================================================
# BACKEND INFORMATION
# ============================================================

with st.expander("Backend Connection Information"):

    st.write(
        "Backend URL:",
        BACKEND_URL,
    )

    st.write(
        "PDF endpoint:",
        f"{BACKEND_URL}/export/pdf",
    )

    st.write(
        "Document available:",
        bool(st.session_state.document),
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "LegalEase — AI-assisted legal document drafting. "
    "Review documents before legal use."
)