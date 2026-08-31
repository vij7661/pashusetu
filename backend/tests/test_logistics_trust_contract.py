from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.core.errors import AppError
from app.logistics.router import delivery, pickup
from app.logistics.schemas import DeliveryRequest, PickupRequest
from app.logistics.service import assert_delivery_weighment_matches_listing
from app.weighment.models import WeighmentSession


class _FakeDb:
    def __init__(self, *, weighment=None):
        self.weighment = weighment
        self.commit_count = 0
        self.flush_count = 0

    def get(self, model, _row_id):
        if model is WeighmentSession:
            return self.weighment
        return None

    def add(self, row):
        if getattr(row, "id", None) is None:
            row.id = uuid4()

    def flush(self):
        self.flush_count += 1

    def commit(self):
        self.commit_count += 1

    def refresh(self, _row):
        pass


def test_delivery_weighment_must_match_listing_target_and_farmer():
    listing = SimpleNamespace(
        target_type="LOT",
        target_id=uuid4(),
        seller_farmer_profile_id=uuid4(),
    )
    matching = SimpleNamespace(
        target_type=listing.target_type,
        target_id=listing.target_id,
        farmer_profile_id=listing.seller_farmer_profile_id,
    )
    assert_delivery_weighment_matches_listing(matching, listing)

    mismatch = SimpleNamespace(
        target_type=listing.target_type,
        target_id=uuid4(),
        farmer_profile_id=listing.seller_farmer_profile_id,
    )
    with pytest.raises(AppError) as exc:
        assert_delivery_weighment_matches_listing(mismatch, listing)
    assert exc.value.code == "DELIVERY_WEIGHMENT_TARGET_MISMATCH"


def test_delivery_validation_failure_does_not_commit_partial_state(monkeypatch):
    user = SimpleNamespace(id=uuid4())
    tx = SimpleNamespace(id=uuid4(), state="IN_TRANSIT")
    weighment = SimpleNamespace(id=uuid4(), weighment_code="WGT-DELIVERY", status="VERIFIED")
    db = _FakeDb(weighment=weighment)
    transitions = []

    monkeypatch.setattr("app.logistics.router.transaction_for_party", lambda *_args: tx)

    def fail_evaluation(*_args):
        raise AppError("DELIVERY_WEIGHMENT_TARGET_MISMATCH", "Mismatch", 409)

    def capture_transition(*args, **kwargs):
        transitions.append((args, kwargs))

    monkeypatch.setattr("app.logistics.router.evaluate_delivery", fail_evaluation)
    monkeypatch.setattr("app.logistics.router.transition_transaction", capture_transition)

    payload = DeliveryRequest(
        qr_verified=True,
        goat_count=3,
        delivery_weighment_id=weighment.id,
    )
    with pytest.raises(AppError) as exc:
        delivery("TX-001", payload, db=db, user=user)

    assert exc.value.code == "DELIVERY_WEIGHMENT_TARGET_MISMATCH"
    assert db.commit_count == 0
    assert db.flush_count == 0
    assert transitions == []
    assert tx.state == "IN_TRANSIT"


def test_pickup_record_transitions_and_audit_commit_once(monkeypatch):
    user = SimpleNamespace(id=uuid4())
    tx = SimpleNamespace(id=uuid4(), state="PICKUP_SCHEDULED")
    db = _FakeDb()
    transitions = []
    events = []

    monkeypatch.setattr("app.logistics.router.transaction_for_party", lambda *_args: tx)

    def capture_transition(_db, received_tx, target, *, commit=True):
        transitions.append((target, commit))
        received_tx.state = target
        return received_tx

    def capture_event(*args, **kwargs):
        events.append((args, kwargs))

    monkeypatch.setattr("app.logistics.router.transition_transaction", capture_transition)
    monkeypatch.setattr("app.logistics.router.append_event", capture_event)

    response = pickup(
        "TX-001",
        PickupRequest(qr_verified=True, goat_count=4),
        db=db,
        user=user,
    )

    assert transitions == [("PICKED_UP", False), ("IN_TRANSIT", False)]
    assert db.flush_count == 1
    assert db.commit_count == 1
    assert response.transaction_state == "IN_TRANSIT"
    assert len(events) == 1
    args, kwargs = events[0]
    assert args[1:5] == ("TRANSACTION", tx.id, "PICKUP_RECORDED", user.id)
    assert kwargs["commit"] is False
