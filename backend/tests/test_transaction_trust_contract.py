from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.core.errors import AppError
from app.transaction.router import create_from_listing


class _FakeDb:
    def __init__(self, scalar_results):
        self._scalar_results = iter(scalar_results)

    def scalar(self, _statement):
        return next(self._scalar_results)

    def get(self, _model, _row_id):
        raise AssertionError("Accepted bid lookup must not happen for an unauthorized farmer")


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
