import hashlib
import json
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.marketplace.models import IdempotencyRecord


def fingerprint(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def get_existing_idempotent_result(
    db: Session,
    actor_user_id: UUID,
    key: str,
    operation: str,
    payload: dict,
):
    fp = fingerprint(payload)
    row = db.scalar(
        select(IdempotencyRecord).where(
            IdempotencyRecord.actor_user_id == actor_user_id,
            IdempotencyRecord.idempotency_key == key,
        )
    )
    if not row:
        return None, fp
    if row.operation != operation or row.request_fingerprint != fp:
        raise AppError(
            "IDEMPOTENCY_KEY_REUSED",
            "Idempotency key was reused with a different operation or payload.",
            409,
        )
    return row, fp


def save_idempotent_result(
    db: Session,
    actor_user_id: UUID,
    key: str,
    operation: str,
    request_fingerprint: str,
    resource_type: str,
    resource_id: UUID,
    response_status: int,
    response_payload: str | None = None,
):
    row = IdempotencyRecord(
        actor_user_id=actor_user_id,
        idempotency_key=key,
        operation=operation,
        request_fingerprint=request_fingerprint,
        resource_type=resource_type,
        resource_id=resource_id,
        response_status=response_status,
        response_payload=response_payload,
    )
    db.add(row)
    db.commit()
    return row
