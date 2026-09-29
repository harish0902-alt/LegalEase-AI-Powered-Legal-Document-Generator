from pydantic import BaseModel, Field, field_validator


class DocumentRequest(BaseModel):
    document_type: str = Field(
        ...,
        min_length=2,
        max_length=120,
    )

    parties: str = Field(
        ...,
        min_length=2,
        max_length=4000,
    )

    terms: str = Field(
        ...,
        min_length=2,
        max_length=10000,
    )

    dates: str = Field(
        ...,
        min_length=2,
        max_length=300,
    )

    @field_validator(
        "document_type",
        "parties",
        "terms",
        "dates",
    )
    @classmethod
    def validate_text(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("This field cannot be empty.")

        return value


class DocumentResponse(BaseModel):
    document_type: str
    content: str
    terms: list[str]
    generated_by: str