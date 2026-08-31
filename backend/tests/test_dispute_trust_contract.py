from types import SimpleNamespace
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.core.errors import AppError
from app.disputes.router import _transaction_or_404
from app.disputes.schemas import EvidenceAddResponse, ReweighAttachResponse
from app.disputes.service import (
    _assert_reweigh_matches_listing,
    _require_open_dispute,
    add_evidence,
    attach_reweigh,
)
from app.marketplace.models import Listing
from app.transaction.models import Transaction


def _listing_target():
    return SimpleNamespace(
        target_type="LOT",
        target_id=uuid4(),
        seller_farmer_profile_id=uuid4(),
    )


class _FakeDb:
    def __init__(self, *, scalar_result=None, transaction=None, listing=None):
        self.scalar_result = scalar_result
        self.transaction = transaction
        self.listing = listing
        self.commit_count = 0
        self.flush_count = 0

    def scalar(self, _statement):
        return self.scalar_result

    def get(self, model, _row_id):
        if model is Transaction:
            return self.transaction
        if model is Listing:
            return self.listing
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


def test_open_dispute_accepts_additional_evidence():
    _require_open_dispute(SimpleNamespace(status="OPEN"))


def test_resolved_dispute_rejects_additional_evidence():
    with pytest.raises(AppError) as exc:
        _require_open_dispute(SimpleNamespace(status="RESOLVED"))
    assert exc.value.code == "DISPUTE_NOT_OPEN"


def test_reweigh_must_match_disputed_listing_target_and_farmer():
    listing = _listing_target()
    matching = SimpleNamespace(
        target_type=listing.target_type,
        target_id=listing.target_id,
        farmer_profile_id=listing.seller_farmer_profile_id,
    )
    _assert_reweigh_matches_listing(matching, listing)

    wrong_target = SimpleNamespace(
        target_type=listing.target_type,
        target_id=uuid4(),
        farmer_profile_id=listing.seller_farmer_profile_id,
    )
    with pytest.raises(AppError) as exc:
        _assert_reweigh_matches_listing(wrong_target, listing)
    assert exc.value.code == "REWEIGH_TARGET_MISMATCH"

    wrong_farmer = SimpleNamespace(
        target_type=listing.target_type,
        target_id=listing.target_id,
        farmer_profile_id=uuid4(),
    )
    with pytest.raises(AppError) as exc:
        _assert_reweigh_matches_listing(wrong_farmer, listing)
    assert exc.value.code == "REWEIGH_TARGET_MISMATCH"


def test_missing_dispute_transaction_returns_domain_404():
    dispute = SimpleNamespace(transaction_id=uuid4())
    with pytest.raises(AppError) as exc:
        _transaction_or_404(_FakeDb(transaction=None), dispute)
    assert exc.value.code == "TRANSACTION_NOT_FOUND"
    assert exc.value.status_code == 404


def test_dispute_mutation_responses_are_strictly_typed():
    evidence = EvidenceAddResponse(evidence_id="E-1", status="RECORDED")
    reweigh = ReweighAttachResponse(
        reweigh_id="RW-1",
        stage="CONTROLLED",
        status="RECORDED",
    )
    assert evidence.status == "RECORDED"
    assert reweigh.stage == "CONTROLLED"

    with pytest.raises(ValidationError):
        EvidenceAddResponse(evidence_id="E-1", status="DONE")
    with pytest.raises(ValidationError):
        ReweighAttachResponse(reweigh_id="RW-1", stage="DELIVERY", status="RECORDED")


def test_dispute_evidence_addition_is_audited_atomically_without_reference(monkeypatch):
    actor_id = uuid4()
    transaction_id = uuid4()
    dispute = SimpleNamespace(
        id=uuid4(),
        status="OPEN",
        transaction_id=transaction_id,
        dispute_code="DSP-TEST",
    )
    calls = []
    db = _FakeDb()

    def capture_event(*args, **kwargs):
        calls.append((args, kwargs))

    monkeypatch.setattr("app.disputes.service.append_event", capture_event)
    add_evidence(db, dispute, actor_id, "PHOTO", "private://evidence/object")

    assert len(calls) == 1
    args, kwargs = calls[0]
    assert args[1:5] == (
        "TRANSACTION",
        transaction_id,
        "DISPUTE_EVIDENCE_ADDED",
        actor_id,
    )
    assert kwargs["payload"]["dispute_id"] == "DSP-TEST"
    assert kwargs["payload"]["evidence_type"] == "PHOTO"
    assert "evidence_reference" not in kwargs["payload"]
    assert kwargs["commit"] is False
    assert db.flush_count == 1
    assert db.commit_count == 1


def test_dispute_reweigh_attachment_is_audited_atomically(monkeypatch):
    actor_id = uuid4()
    transaction_id = uuid4()
    listing = _listing_target()
    weighment = SimpleNamespace(
        id=uuid4(),
        weighment_code="WGT-TEST-001",
        status="VERIFIED",
        target_type=listing.target_type,
        target_id=listing.target_id,
        farmer_profile_id=listing.seller_farmer_profile_id,
    )
    transaction = SimpleNamespace(listing_id=uuid4())
    dispute = SimpleNamespace(
        id=uuid4(),
        status="OPEN",
        transaction_id=transaction_id,
        dispute_code="DSP-TEST",
    )
    db = _FakeDb(scalar_result=weighment, transaction=transaction, listing=listing)
    calls = []

    def capture_event(*args, **kwargs):
        calls.append((args, kwargs))

    monkeypatch.setattr("app.disputes.service.append_event", capture_event)
    attach_reweigh(db, dispute, actor_id, weighment.weighment_code, "CONTROLLED")

    assert len(calls) == 1
    args, kwargs = calls[0]
    assert args[1:5] == (
        "TRANSACTION",
        transaction_id,
        "DISPUTE_REWEIGH_ATTACHED",
        actor_id,
    )
    assert kwargs["payload"]["dispute_id"] == "DSP-TEST"
    assert kwargs["payload"]["weighment_code"] == "WGT-TEST-001"
    assert kwargs["payload"]["stage"] == "CONTROLLED"
    assert kwargs["commit"] is False
    assert db.flush_count == 1
    assert db.commit_count == 1
