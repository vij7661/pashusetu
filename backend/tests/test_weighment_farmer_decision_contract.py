from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

from pydantic import ValidationError
import pytest

from app.weighment import service as weighment_service
from app.weighment.schemas import AcknowledgeResponse


class FakeDb:
    def __init__(self, scalar_values=None):
        self.commit_count = 0
        self.flush_count = 0
        self.scalar_values = list(scalar_values or [])
        self.added = []

    def scalar(self, _query):
        return self.scalar_values.pop(0)

    def add(self, value):
        self.added.append(value)

    def flush(self):
        self.flush_count += 1

    def commit(self):
        self.commit_count += 1

    def refresh(self, _value):
        return None


def _capture_audit(monkeypatch):
    events = []

    def fake_append_event(
        db,
        aggregate_type,
        aggregate_id,
        event_type,
        actor_user_id=None,
        request_id=None,
        payload=None,
        *,
        commit=True,
    ):
        events.append(
            {
                "aggregate_type": aggregate_type,
                "aggregate_id": aggregate_id,
                "event_type": event_type,
                "actor_user_id": actor_user_id,
                "payload": payload,
                "commit": commit,
            }
        )
        db.flush()
        return SimpleNamespace()

    monkeypatch.setattr(weighment_service, "append_event", fake_append_event)
    return events


def test_farmer_acceptance_is_atomic_audited_domain_outcome(monkeypatch):
    db = FakeDb()
    session = SimpleNamespace(
        id=uuid4(),
        status="FARMER_REVIEW",
        farmer_profile_id=uuid4(),
    )
    actor_user_id = uuid4()
    events = _capture_audit(monkeypatch)

    acknowledgement = weighment_service.acknowledge_weighment(
        db,
        session,
        acknowledged=True,
        method="APP_CONFIRMATION",
        actor_user_id=actor_user_id,
    )

    assert acknowledgement is not None
    assert acknowledgement.acknowledged is True
    assert session.status == "ACKNOWLEDGED"
    assert db.commit_count == 1
    assert events == [
        {
            "aggregate_type": "WEIGHMENT",
            "aggregate_id": session.id,
            "event_type": "FARMER_WEIGHMENT_ACKNOWLEDGED",
            "actor_user_id": actor_user_id,
            "payload": {"method": "APP_CONFIRMATION", "status": "ACKNOWLEDGED"},
            "commit": False,
        }
    ]


def test_farmer_rejection_is_atomic_audited_domain_outcome(monkeypatch):
    db = FakeDb()
    session = SimpleNamespace(id=uuid4(), status="FARMER_REVIEW")
    actor_user_id = uuid4()
    events = _capture_audit(monkeypatch)

    acknowledgement = weighment_service.acknowledge_weighment(
        db,
        session,
        acknowledged=False,
        method="APP_CONFIRMATION",
        actor_user_id=actor_user_id,
    )

    assert acknowledgement is None
    assert session.status == "REJECTED_BY_FARMER"
    assert db.commit_count == 1
    assert events == [
        {
            "aggregate_type": "WEIGHMENT",
            "aggregate_id": session.id,
            "event_type": "FARMER_WEIGHMENT_REJECTED",
            "actor_user_id": actor_user_id,
            "payload": {"method": "APP_CONFIRMATION", "status": "REJECTED_BY_FARMER"},
            "commit": False,
        }
    ]


def test_receipt_creation_and_audit_share_one_commit(monkeypatch):
    locked = SimpleNamespace(net_kg=Decimal("12.500"))
    db = FakeDb([locked, None])
    session = SimpleNamespace(
        id=uuid4(),
        status="ACKNOWLEDGED",
        weighment_code="WG-TEST",
        scale_id=uuid4(),
    )
    actor_user_id = uuid4()
    events = _capture_audit(monkeypatch)

    receipt = weighment_service.create_receipt(
        db,
        session,
        actor_user_id=actor_user_id,
    )

    assert receipt.receipt_code.startswith("RCPT-")
    assert session.status == "VERIFIED"
    assert db.commit_count == 1
    assert events[0]["event_type"] == "WEIGHMENT_RECEIPT_CREATED"
    assert events[0]["actor_user_id"] == actor_user_id
    assert events[0]["commit"] is False


def test_acknowledge_response_contract_matches_real_session_states():
    accepted = AcknowledgeResponse(
        acknowledgement_id="ack-1",
        status="ACKNOWLEDGED",
    )
    rejected = AcknowledgeResponse(
        acknowledgement_id=None,
        status="REJECTED_BY_FARMER",
    )

    assert accepted.status == "ACKNOWLEDGED"
    assert rejected.status == "REJECTED_BY_FARMER"

    with pytest.raises(ValidationError):
        AcknowledgeResponse(
            acknowledgement_id="ack-1",
            status="ACKNOWLEDGED_BY_FARMER",
        )
