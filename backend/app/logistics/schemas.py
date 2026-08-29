from pydantic import BaseModel, Field


class TransportAssignRequest(BaseModel):
    transporter_name: str
    driver_name: str
    driver_phone: str
    vehicle_number: str


class PickupRequest(BaseModel):
    qr_verified: bool
    goat_count: int = Field(gt=0)
    loading_video_evidence_id: str
    departure_note: str | None = None
    idempotency_key: str = Field(min_length=8, max_length=120)


class DeliveryRequest(BaseModel):
    qr_verified: bool
    goat_count: int = Field(gt=0)
    delivery_video_evidence_id: str
    delivery_weighment_id: str
    idempotency_key: str = Field(min_length=8, max_length=120)


class ToleranceResult(BaseModel):
    origin_weight_kg: float
    delivery_weight_kg: float
    difference_kg: float
    difference_percent: float
    allowed_percent: float
    within_tolerance: bool
    route: str
