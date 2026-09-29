from __future__ import annotations

import re
import time
from typing import Optional

from backend.config import get_settings


_RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
_MAX_GENERATION_ATTEMPTS = 3


def _is_retryable_api_error(error: Exception) -> bool:
    status_code = getattr(error, "code", None)
    if status_code is None:
        status_code = getattr(error, "status_code", None)

    try:
        if int(status_code) in _RETRYABLE_STATUS_CODES:
            return True
    except (TypeError, ValueError):
        pass

    return bool(
        re.search(
            r"\b(?:429|500|502|503|504|UNAVAILABLE|RESOURCE_EXHAUSTED|high demand)\b",
            str(error),
            re.IGNORECASE,
        )
    )


class GeminiLegalGenerator:
    """
    Generates legal document drafts using Gemini.

    When MOCK_AI=true in .env, the application does not
    call Gemini and instead creates a sample document.
    """

    def __init__(self):
        self.settings = get_settings()
        self._client = None

        if (
            not self.settings.mock_ai
            and self.settings.gemini_api_key
        ):
            try:
                from google import genai

                self._client = genai.Client(
                    api_key=self.settings.gemini_api_key
                )

            except Exception as exc:
                raise RuntimeError(
                    "Could not initialize Gemini client: "
                    f"{exc}"
                ) from exc

    @property
    def generated_by(self) -> str:
        """
        Returns the source used to generate the document.
        """

        if self.settings.mock_ai:
            return "Mock AI"

        return "Google Gemini"

    def generate(
        self,
        document_type: str,
        parties: str,
        terms: str,
        dates: str,
    ) -> str:
        """
        Generate a legal document.
        """

        if self.settings.mock_ai:
            return self._generate_mock(
                document_type=document_type,
                parties=parties,
                terms=terms,
                dates=dates,
            )

        return self._generate_gemini(
            document_type=document_type,
            parties=parties,
            terms=terms,
            dates=dates,
        )

    # ========================================================
    # GEMINI
    # ========================================================

    def _generate_gemini(
        self,
        document_type: str,
        parties: str,
        terms: str,
        dates: str,
    ) -> str:

        if not self.settings.gemini_api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured. "
                "Either add your Gemini API key to .env "
                "or set MOCK_AI=true."
            )

        if self._client is None:
            raise RuntimeError(
                "Gemini client is not initialized."
            )

        prompt = f"""
You are a legal document drafting assistant.

Draft a professional legal document based on the
information below.

IMPORTANT:
- This is an AI-assisted draft.
- Do not invent important facts.
- Use clear and professional legal language.
- Preserve the supplied parties, terms, and dates.
- Organize the document with clear headings.
- Include appropriate signature sections.
- Do not claim that the document is legally reviewed.
- Do not provide false legal guarantees.

DOCUMENT TYPE:
{document_type}

PARTIES:
{parties}

TERMS:
{terms}

DATES:
{dates}

Return only the document draft.
"""

        primary_model = self.settings.gemini_model
        fallback_models = [
            m
            for m in getattr(self.settings, "fallback_model_list", [])
            if m and m != primary_model
        ]
        models_to_try = [primary_model] + fallback_models

        last_error = None
        response = None

        for model_idx, model_name in enumerate(models_to_try):
            max_attempts = (
                _MAX_GENERATION_ATTEMPTS
                if len(models_to_try) == 1
                else 2
            )
            for attempt in range(max_attempts):
                try:
                    response = self._client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                    )
                    break
                except Exception as exc:
                    last_error = exc
                    if not _is_retryable_api_error(exc):
                        raise RuntimeError(
                            f"Gemini API request failed: {exc}"
                        ) from exc

                    is_last_attempt = (
                        attempt == max_attempts - 1
                    )
                    is_last_model = (
                        model_idx == len(models_to_try) - 1
                    )

                    if is_last_attempt and is_last_model:
                        break

                    time.sleep(2 ** attempt)

            if response is not None:
                break

        if response is None:
            raise RuntimeError(
                f"Gemini API request failed: {last_error}"
            ) from last_error

        text: Optional[str] = getattr(
            response,
            "text",
            None,
        )

        if not text:
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return text.strip()

    # ========================================================
    # MOCK AI
    # ========================================================

    def _generate_mock(
        self,
        document_type: str,
        parties: str,
        terms: str,
        dates: str,
    ) -> str:

        clean_terms = [
            item.strip()
            for item in terms.replace(
                ";",
                "\n",
            ).splitlines()
            if item.strip()
        ]

        terms_text = ""

        if clean_terms:

            terms_text = "\n".join(
                f"{index}. {term}"
                for index, term in enumerate(
                    clean_terms,
                    start=1,
                )
            )

        else:

            terms_text = (
                "1. The parties agree to the terms "
                "described in this agreement."
            )

        document = f"""
{document_type.upper()}

This document is an AI-assisted draft prepared
using LegalEase.

PARTIES

{parties}

EFFECTIVE DATES

{dates}

AGREEMENT

The parties identified above agree to enter into
this {document_type} subject to the terms and
conditions described below.

KEY TERMS

{terms_text}

GENERAL PROVISIONS

1. The parties agree to perform their respective
   obligations in good faith.

2. Any amendment to this document should be made
   in writing and agreed to by the parties.

3. The parties should comply with applicable laws
   and regulations.

4. This document should be reviewed by an
   appropriately qualified legal professional
   before being relied upon.

CONFIDENTIALITY

The parties should maintain the confidentiality
of information that is identified as confidential,
subject to applicable law and any agreed exceptions.

TERMINATION

The parties may terminate this agreement according
to the termination terms agreed between them.

SIGNATURES

Party 1:

Name: ______________________________

Signature: ___________________________

Date: _______________________________


Party 2:

Name: ______________________________

Signature: ___________________________

Date: _______________________________


DISCLAIMER

This document is an AI-assisted draft generated
by LegalEase. It is not a substitute for legal
advice or professional legal review.
""".strip()

        return document