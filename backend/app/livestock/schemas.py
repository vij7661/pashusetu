from typing import Literal

from pydantic import BaseModel, Field


class GoatCreate(BaseModel):
    breed: str | None = Field(default=None, max_length=80)
    sex: Literal["MALE", "FEMALE", "UNKNOWN"] | None = None
    age_months: int | None = Field(default=None, ge=0, le=300)
    health_notes: str | None = Field(default=None, max_length=2000)


class GoatResponse(BaseModel):
    goat_id: str
    breed: str | None
    sex: str | None
    age_months: int | None
    health_notes: str | None
    status: str


class LotCreate(BaseModel):
    declared_quantity: int = Field(gt=0, le=500)
    breed_summary: str | None = Field(default=None, max_length=160)
    sex_summary: str | None = Field(default=None, max_length=160)
    age_summary: str | None = Field(default=None, max_length=160)
    health_notes: str | None = Field(default=None, max_length=2000)
    goat_ids: list[str] = Field(default_factory=list)


class LotResponse(BaseModel):
    lot_id: str
    declared_quantity: int
    linked_goat_ids: list[str]
    breed_summary: str | None
    sex_summary: str | None
    age_summary: str | None
    status: str


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
    evidence_id: str
    storage_key: str
    upload_method: str
    upload_url: str
    expires_in_seconds: int
