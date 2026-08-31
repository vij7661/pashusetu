from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.core.errors import AppError
from app.transaction.router import create_from_listing
from app.transaction.service import create_transaction_from_accepted_bid


class _FakeDb:
    def __init__(self, scalar_results):
        self._scalar_results = iter(scalar_results)
        self.commit_count = 0
        self.flush_count = 0

    def scalar(self, _statement):
        return next(self._scalar_results)

    def get(self, _model, _row_id):
        raise AssertionError("Accepted bid lookup must not happen for an unauthorized farmer")

    def add(self, row):
        if getattr(row, "id", None) is None:
            row.id = uuid4()

    def flush(self):
        self.flush_count += 1

    def commit(self):
        self.commit_count += 1

    def refresh(self, _row):
        pass


def test_transaction_creation_authorizes_farmer_before_mutation(monkeypatch):
    owner_farmer_id = uuid4()
    listing = SimpleNamespace(
        listing_code="LST-001",
        seller_farmer_profile_id=owner_farmer_id,
        status="OFFER_ACCEPTED",
        accepted_bid_id=uuid4(),
    )
    different_farmer = SimpleNamespace(id=uuid4())
    user = SimpleNamespace(id=uuid4())
    db = _FakeDb([listing, different_farmer])
    mutation_called = False

    def fail_if_mutated(*_args, **_kwargs):
        nonlocal mutation_called
        mutation_called = True
        raise AssertionError("Unauthorized request reached transaction mutation")

    monkeypatch.setattr(
        "app.transaction.router.create_transaction_from_accepted_bid",
        fail_if_mutated,
    )

    with pytest.raises(AppError) as exc:
        create_from_listing("LST-001", db=db, user=user)

    assert exc.value.code == "FORBIDDEN"
    assert mutation_called is False


def test_transaction_creation_and_audit_share_one_commit(monkeypatch):
    actor_user_id = uuid4()
    listing = SimpleNamespace(
        id=uuid4(),
        listing_code="LST-001",
        seller_farmer_profile_id=uuid4(),
    )
    bid = SimpleNamespace(
        id=uuid4(),
        bid_code="BID-001",
        buyer_profile_id=uuid4(),
    )
    db = _FakeDb([None])
    events = []

    def capture_event(*args, **kwargs):
        events.append((args, kwargs))

    monkeypatch.setattr("app.transaction.service.append_event", capture_event)

    tx = create_transaction_from_accepted_bid(db, listing, bid, actor_user_id)

    assert tx.listing_id == listing.id
    assert tx.accepted_bid_id == bid.id
    assert db.flush_count == 1
    assert db.commit_count == 1
    assert len(events) == 1
    args, kwargs = events[0]
    assert args[1:5] == ("TRANSACTION", tx.id, "TRANSACTION_CREATED", actor_user_id)
    assert kwargs["payload"] == {
        "transaction_id": tx.transaction_code,
        "listing_id": "LST-001",
        "accepted_bid_id": "BID-001",
    }
    assert kwargs["commit"] is False
