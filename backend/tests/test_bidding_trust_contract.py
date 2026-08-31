from types import SimpleNamespace
from uuid import uuid4

from app.bidding.router import post_accept_bid
from app.bidding.service import accept_bid


class _ScalarRows:
    def __init__(self, rows):
        self._rows = rows

    def all(self):
        return self._rows


class _AcceptBidDb:
    def __init__(self, scalar_results, other_bids=None):
        self._scalar_results = iter(scalar_results)
        self._other_bids = other_bids or []
        self.flush_count = 0
        self.commit_count = 0
        self.refreshed = []

    def scalar(self, _statement):
        return next(self._scalar_results)

    def scalars(self, _statement):
        return _ScalarRows(self._other_bids)

    def get(self, _model, _row_id):
        return None

    def flush(self):
        self.flush_count += 1

    def commit(self):
        self.commit_count += 1

    def refresh(self, row):
        self.refreshed.append(row)


class _RouterDb:
    def __init__(self):
        self.commit_count = 0
        self.refreshed = []

    def commit(self):
        self.commit_count += 1

    def refresh(self, row):
        self.refreshed.append(row)


def test_bid_acceptance_audit_stays_uncommitted_for_atomic_composition(monkeypatch):
    farmer_user_id = uuid4()
    farmer = SimpleNamespace(id=uuid4())
    listing = SimpleNamespace(
        id=uuid4(),
        listing_code="LST-001",
        seller_farmer_profile_id=farmer.id,
        accepted_bid_id=None,
        status="PUBLISHED",
    )
    bid = SimpleNamespace(
        id=uuid4(),
        bid_code="BID-001",
        listing_id=listing.id,
        status="ACTIVE",
        server_sequence=7,
    )
    db = _AcceptBidDb([farmer, listing, bid, bid])
    events = []

    def capture_event(*args, **kwargs):
        events.append((args, kwargs))

    monkeypatch.setattr("app.bidding.service.append_event", capture_event)

    accepted_listing, accepted_bid = accept_bid(
        db,
        farmer_user_id,
        listing.listing_code,
        bid.bid_code,
        commit=False,
    )

    assert accepted_listing.status == "OFFER_ACCEPTED"
    assert accepted_listing.accepted_bid_id == bid.id
    assert accepted_bid.status == "ACCEPTED"
    assert db.flush_count == 1
    assert db.commit_count == 0
    assert len(events) == 1
    args, kwargs = events[0]
    assert args[1:5] == ("LISTING", listing.id, "BID_ACCEPTED", farmer_user_id)
    assert kwargs["payload"] == {
        "listing_id": "LST-001",
        "accepted_bid_id": "BID-001",
        "accepted_server_sequence": 7,
    }
    assert kwargs["commit"] is False


def test_accept_endpoint_commits_bid_and_transaction_once(monkeypatch):
    user = SimpleNamespace(id=uuid4())
    listing = SimpleNamespace(
        listing_code="LST-001",
        status="OFFER_ACCEPTED",
    )
    bid = SimpleNamespace(
        bid_code="BID-001",
        server_sequence=7,
    )
    db = _RouterDb()
    calls = []

    def fake_accept(_db, actor_id, listing_id, bid_id, *, commit=True):
        calls.append(("accept", actor_id, listing_id, bid_id, commit))
        return listing, bid

    def fake_create(_db, received_listing, received_bid, actor_id, *, commit=True):
        calls.append(("transaction", received_listing, received_bid, actor_id, commit))
        return SimpleNamespace()

    monkeypatch.setattr("app.bidding.router.accept_bid", fake_accept)
    monkeypatch.setattr("app.bidding.router.create_transaction_from_accepted_bid", fake_create)

    response = post_accept_bid("LST-001", "BID-001", db=db, user=user)

    assert calls[0] == ("accept", user.id, "LST-001", "BID-001", False)
    assert calls[1] == ("transaction", listing, bid, user.id, False)
    assert db.commit_count == 1
    assert db.refreshed == [listing, bid]
    assert response.status == "OFFER_ACCEPTED"
