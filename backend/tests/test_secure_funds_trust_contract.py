from types import SimpleNamespace
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.core.errors import AppError
from app.payments.router import secure
from app.payments.schemas import SecureFundsResponse


class _FakeDb:
    def __init__(self, bid=None):
        self.bid = bid
        self.added = []
        self.flush_count = 0
        self.commit_count = 0
        self.refresh_count = 0

    def get(self, _model, _row_id):
        return self.bid

    def add(self, row):
        self.added.append(row)
        if getattr(row, "id", None) is None:
            row.id = uuid4()

    def flush(self):
        self.flush_count += 1

    def commit(self):
        self.commit_count += 1

    def refresh(self, _row):
        self.refresh_count += 1


def test_secure_funds_response_is_strictly_typed():
    response = SecureFundsResponse(
        payment_intent_id=str(uuid4()),
        provider_reference="SIM-ABC123",
        amount_paise=125_000,
        status="SECURED",
        transaction_state="FUNDS_SECURED",
    )
    assert response.status == "SECURED"

    with pytest.raises(ValidationError):
        SecureFundsResponse(
            payment_intent_id=str(uuid4()),
            provider_reference="SIM-ABC123",
            amount_paise=125_000,
            status="PENDING",
            transaction_state="FUNDS_SECURED",
        )


def test_secure_funds_rejects_missing_accepted_bid(monkeypatch):
    tx = SimpleNamespace(id=uuid4(), state="AGREEMENT_LOCKED", accepted_bid_id=uuid4())
    user = SimpleNamespace(id=uuid4())
    db = _FakeDb(bid=None)
    monkeypatch.setattr("app.payments.router.transaction_for_party", lambda *_args: tx)

    with pytest.raises(AppError) as exc_info:
        secure("TX-TEST", db=db, user=user)

    assert exc_info.value.code == "ACCEPTED_BID_NOT_FOUND"
    assert db.commit_count == 0


def test_secure_funds_domain_state_and_audit_share_one_commit(monkeypatch):
    bid = SimpleNamespace(id=uuid4(), total_offer_paise=125_000)
    tx = SimpleNamespace(
        id=uuid4(),
        state="AGREEMENT_LOCKED",
        accepted_bid_id=bid.id,
        transaction_code="TX-TEST",
    )
    user = SimpleNamespace(id=uuid4())
    db = _FakeDb(bid=bid)
    transitions = []
    events = []

    monkeypatch.setattr("app.payments.router.transaction_for_party", lambda *_args: tx)

    def capture_transition(_db, received_tx, state, *, commit=True):
        transitions.append((received_tx, state, commit))
        received_tx.state = state
        return received_tx

    def capture_event(*args, **kwargs):
        events.append((args, kwargs))

    monkeypatch.setattr("app.payments.router.transition_transaction", capture_transition)
    monkeypatch.setattr("app.payments.router.append_event", capture_event)

    response = secure("TX-TEST", db=db, user=user)

    assert response.amount_paise == 125_000
    assert response.status == "SECURED"
    assert response.transaction_state == "FUNDS_SECURED"
    assert transitions == [(tx, "FUNDS_SECURED", False)]
    assert db.flush_count == 1
    assert db.commit_count == 1
    assert db.refresh_count == 1
    assert len(events) == 1
    args, kwargs = events[0]
    assert args[1:5] == ("TRANSACTION", tx.id, "FUNDS_SECURED", user.id)
    assert kwargs["payload"]["amount_paise"] == 125_000
    assert kwargs["commit"] is False
