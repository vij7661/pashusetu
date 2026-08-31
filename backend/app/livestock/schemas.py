from typing import Literal

from pydantic import BaseModel, Field, model_validator


class GoatCreate(BaseModel):
    breed: str | None = Field(default=None, max_length=80)
    sex: Literal["MALE", "FEMALE", "UNKNOWN"] | None = None
    age_months: int | None = Field(default=None, ge=0, le=300)
    health_notes: str | None = Field(default=None, max_length=2000)


class GoatResponse(BaseModel):
    goat_id: str = Field(min_length=1)
    breed: str | None
    sex: Literal["MALE", "FEMALE", "UNKNOWN"] | None
    age_months: int | None = Field(default=None, ge=0, le=300)
    health_notes: str | None
    status: str = Field(min_length=1)


class LotCreate(BaseModel):
    declared_quantity: int = Field(gt=0, le=500)
    breed_summary: str | None = Field(default=None, max_length=160)
    sex_summary: str | None = Field(default=None, max_length=160)
    age_summary: str | None = Field(default=None, max_length=160)
    health_notes: str | None = Field(default=None, max_length=2000)
    goat_ids: list[str] = Field(default_factory=list)


class LotResponse(BaseModel):
    lot_id: str = Field(min_length=1)
    declared_quantity: int = Field(gt=0, le=500)
    linked_goat_ids: list[str]
    breed_summary: str | None
    sex_summary: str | None
    age_summary: str | None
    status: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_linked_quantity(self):
        if any(not goat_id for goat_id in self.linked_goat_ids):
            raise ValueError("linked_goat_ids cannot contain blank identifiers")
        if len(self.linked_goat_ids) > self.declared_quantity:
            raise ValueError("linked goats cannot exceed declared quantity")
        return self


class EvidenceUploadRequest(BaseModel):
    owner_type: Literal["GOAT", "LOT"]
    owner_id: str
    evidence_type: Literal[
        "PHOTO_FRONT",
        "PHOTO_SIDE",
        "PHOTO_REAR",
        "PHOTO_TAG",
        "HEALTH_DOC",
        "OTHER",
    ]
    file_name: str = Field(min_length=1, max_length=255)
    mime_type: str = Field(min_length=3, max_length=120)


class EvidenceUploadResponse(BaseModel):
    evidence_id: str = Field(min_length=1)
    storage_key: str = Field(min_length=1)
    upload_method: Literal["PUT"]
    upload_url: str = Field(min_length=1)
    expires_in_seconds: int = Field(gt=0)
