from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class WeighmentStartRequest(BaseModel):
    target_type: Literal["GOAT", "LOT"]
    target_id: str
    scale_code: str


class WeighmentSessionResponse(BaseModel):
    weighment_id: str
    target_type: str
    target_id: str
    centre_code: str
    operator_code: str
    scale_code: str
    status: str
    reweigh_of_id: str | None = None


class ReadingCreate(BaseModel):
    gross_kg: Decimal = Field(gt=0, decimal_places=3)
    tare_kg: Decimal = Field(ge=0, decimal_places=3)
    stable: bool = False

    @model_validator(mode="after")
    def validate_weight(self):
        if self.tare_kg >= self.gross_kg:
            raise ValueError("tare_kg must be less than gross_kg")
        return self


class ReadingResponse(BaseModel):
    reading_id: str
    sequence_no: int
    gross_kg: Decimal
    tare_kg: Decimal
    net_kg: Decimal
    stable: bool
    locked: bool


class LockReadingRequest(BaseModel):
    reading_id: str


class VerificationEvidenceRequest(BaseModel):
    video_evidence_id: str


class AcknowledgeRequest(BaseModel):
    acknowledged: bool = True
    method: Literal["APP_CONFIRMATION", "OPERATOR_ASSISTED"] = "APP_CONFIRMATION"


class ReceiptResponse(BaseModel):
    receipt_id: str
    receipt_code: str
    qr_payload: str
    print_status: str
    target_type: Literal["GOAT", "LOT"]
    target_id: str


class ReweighRequest(BaseModel):
    scale_code: str
