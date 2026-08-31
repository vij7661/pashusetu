from types import SimpleNamespace
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.agreement.schemas import (
    PILOT_DISPUTE_RULE,
    PILOT_PRICE_BASIS,
    PILOT_TRANSPORT_RESPONSIBILITY,
    AgreementCreate,
)
from app.agreement.service import confirm_agreement, create_agreement


class _FakeAgreementDb:
    def __init__(self, accepted_bid, next_version=1):
        self.accepted_bid = accepted_bid
        self.next_version = next_version
        self.flush_count = 0
        self.commit_count = 0

    def get(self, _model, _row_id):
        return self.accepted_bid

    def scalar(self, _statement):
        return self.next_version

    def add(self, row):
        if getattr(row, "id", None) is None:
            row.id = uuid4()

    def flush(self):
        self.flush_count += 1

    def commit(self):
        self.commit_count += 1

    def refresh(self, _row):
        pass


class _ScalarsResult:
    def __init__(self, rows):
        self._rows = rows

    def all(self):
        return self._rows


class _FakeConfirmationDb:
    def __init__(self, confirmed_roles):
        self.confirmed_roles = confirmed_roles
        self.flush_count = 0
        self.commit_count = 0
        self.added = []

    def scalar(self, _statement):
        return None

    def add(self, row):
        if getattr(row, "id", None) is None:
            row.id = uuid4()
        self.added.append(row)

    def flush(self):
        self.flush_count += 1

    def scalars(self, _statement):
        return _ScalarsResult(
            [SimpleNamespace(party_role=role) for role in self.confirmed_roles]
        )

    def commit(self):
        self.commit_count += 1

    def refresh(self, _row):
        pass


def test_farmer_agreement_payload_contains_only_transaction_specific_inputs():
    payload = AgreementCreate(
        pickup_point="Verified pickup point",
        final_weighing_point="Verified final scale",
        tolerance_percent=1.5,
    )

    assert payload.model_dump() == {
        "pickup_point": "Verified pickup point",
        "final_weighing_point": "Verified final scale",
        "tolerance_percent": 1.5,
    }


def test_client_cannot_override_server_owned_pilot_business_terms():
    with pytest.raises(ValidationError):
        AgreementCreate(
            pickup_point="Verified pickup point",
            final_weighing_point="Verified final scale",
            tolerance_percent=1.5,
            price_basis="ORIGIN_VERIFIED_WEIGHT",
            transport_responsibility="FARMER",
            dispute_rule="Client supplied rule must not become commercial truth.",
        )


def test_pilot_business_terms_are_explicit_backend_constants():
    assert PILOT_PRICE_BASIS == "DELIVERY_ADJUSTED_NET_KG"
    assert PILOT_TRANSPORT_RESPONSIBILITY == "BUYER"
    assert PILOT_DISPUTE_RULE


def test_farmer_agreement_creation_and_audit_share_one_commit(monkeypatch):
    user_id = uuid4()
    accepted_bid = SimpleNamespace(id=uuid4())
    tx = SimpleNamespace(
        id=uuid4(),
        accepted_bid_id=accepted_bid.id,
        state="OFFER_ACCEPTED",
    )
    db = _FakeAgreementDb(accepted_bid)
    payload = AgreementCreate(
        pickup_point="Verified pickup point",
        final_weighing_point="Verified final scale",
        tolerance_percent=1.5,
    )
    transitions = []
    events = []

    monkeypatch.setattr("app.agreement.service._role_for_user", lambda *_args: "FARMER")

    def capture_transition(_db, received_tx, state, *, commit=True):
        transitions.append((received_tx, state, commit))
        received_tx.state = state
        return received_tx

    def capture_event(*args, **kwargs):
        events.append((args, kwargs))

    monkeypatch.setattr("app.agreement.service.transition_transaction", capture_transition)
    monkeypatch.setattr("app.agreement.service.append_event", capture_event)

    agreement = create_agreement(db, tx, user_id, payload)

    assert agreement.version == 1
    assert transitions == [(tx, "AGREEMENT_PENDING", False)]
    assert db.flush_count == 1
    assert db.commit_count == 1
    assert len(events) == 1
    args, kwargs = events[0]
    assert args[1:5] == ("TRANSACTION", tx.id, "AGREEMENT_CREATED", user_id)
    assert kwargs["payload"] == {
        "agreement_id": agreement.agreement_code,
        "version": 1,
    }
    assert kwargs["commit"] is False


def test_agreement_lock_confirmation_and_audit_share_one_commit(monkeypatch):
    user_id = uuid4()
    tx = SimpleNamespace(id=uuid4(), state="AGREEMENT_PENDING", active_agreement_id=None)
    agreement = SimpleNamespace(
        id=uuid4(),
        agreement_code="AGR-TEST",
        version=2,
        locked=False,
        status="PENDING_CONFIRMATION",
    )
    db = _FakeConfirmationDb(["FARMER", "BUYER"])
    transitions = []
    events = []

    monkeypatch.setattr("app.agreement.service._role_for_user", lambda *_args: "BUYER")

    def capture_transition(_db, received_tx, state, *, commit=True):
        transitions.append((received_tx, state, commit))
        received_tx.state = state
        return received_tx

    def capture_event(*args, **kwargs):
        events.append((args, kwargs))

    monkeypatch.setattr("app.agreement.service.transition_transaction", capture_transition)
    monkeypatch.setattr("app.agreement.service.append_event", capture_event)

    result = confirm_agreement(db, tx, agreement, user_id, True)

    assert result is agreement
    assert agreement.locked is True
    assert agreement.status == "LOCKED"
    assert tx.active_agreement_id == agreement.id
    assert transitions == [(tx, "AGREEMENT_LOCKED", False)]
    assert db.flush_count == 1
    assert db.commit_count == 1
    assert [args[3] for args, _kwargs in events] == [
        "AGREEMENT_CONFIRMATION_RECORDED",
        "AGREEMENT_LOCKED",
    ]
    assert all(kwargs["commit"] is False for _args, kwargs in events)
