from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class TransportAssignRequest(BaseModel):
    transporter_name: str
    driver_name: str
    driver_phone: str
    vehicle_number: str


class PickupRequest(BaseModel):
    qr_verified: bool
    goat_count: int = Field(gt=0)
    loading_video_evidence_id: UUID | None = None
    departure_note: str | None = None


class DeliveryRequest(BaseModel):
    qr_verified: bool
    goat_count: int = Field(gt=0)
    delivery_video_evidence_id: UUID | None = None
    delivery_weighment_id: UUID


class TransportAssignResponse(BaseModel):
    assignment_id: str
    transaction_state: Literal["PICKUP_SCHEDULED"]


class PickupResponse(BaseModel):
    pickup_id: str
    transaction_state: Literal["IN_TRANSIT"]


class ToleranceResult(BaseModel):
    origin_weight_kg: float
    delivery_weight_kg: float
    difference_kg: float
    difference_percent: float
    allowed_percent: float
    within_tolerance: bool
    route: Literal["SETTLEMENT", "DISPUTE"]
