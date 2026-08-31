from types import SimpleNamespace
from uuid import uuid4

from app.payments.settlement_service import create_settlement


class _FakeSettlementDb:
    def __init__(self, bid):
        self._scalar_results = iter([None, None])
        self.bid = bid
        self.flush_count = 0
        self.commit_count = 0
        self.added = []

    def scalar(self, _statement):
        return next(self._scalar_results)

    def get(self, _model, _row_id):
        return self.bid

    def add(self, row):
        if getattr(row, "id", None) is None:
            row.id = uuid4()
        self.added.append(row)

    def flush(self):
        self.flush_count += 1

    def commit(self):
        self.commit_count += 1

    def refresh(self, _row):
        pass


def test_settlement_state_audit_reputation_and_close_share_one_commit(monkeypatch):
    actor_user_id = uuid4()
    bid = SimpleNamespace(id=uuid4(), total_offer_paise=100_000)
    tx = SimpleNamespace(
        id=uuid4(),
        accepted_bid_id=bid.id,
        farmer_profile_id=uuid4(),
        buyer_profile_id=uuid4(),
        state="RESOLVED",
    )
    db = _FakeSettlementDb(bid)
    transitions = []
    reputation_calls = []
    events = []

    def capture_transition(_db, received_tx, state, *, commit=True):
        transitions.append((state, commit))
        received_tx.state = state
        return received_tx

    def capture_reputation(_db, received_tx, dispute_loser=None, *, commit=True):
        reputation_calls.append((received_tx, dispute_loser, commit))

    def capture_event(*args, **kwargs):
        events.append((args, kwargs))

    monkeypatch.setattr(
        "app.payments.settlement_service.transition_transaction",
        capture_transition,
    )
    monkeypatch.setattr(
        "app.payments.settlement_service.close_transaction_reputation",
        capture_reputation,
    )
    monkeypatch.setattr(
        "app.payments.settlement_service.append_event",
        capture_event,
    )

    settlement = create_settlement(
        db,
        tx,
        actor_user_id,
        platform_fee_basis_points=0,
    )

    assert settlement.status == "COMPLETED"
    assert settlement.final_amount_paise == 100_000
    assert transitions == [("SETTLED", False), ("CLOSED", False)]
    assert reputation_calls == [(tx, None, False)]
    assert db.commit_count == 1
    assert db.flush_count == 1
    assert len(events) == 2

    settlement_args, settlement_kwargs = events[0]
    assert settlement_args[1:5] == (
        "TRANSACTION",
        tx.id,
        "SETTLEMENT_COMPLETED",
        actor_user_id,
    )
    assert settlement_kwargs["commit"] is False

    close_args, close_kwargs = events[1]
    assert close_args[1:5] == ("TRANSACTION", tx.id, "TRANSACTION_CLOSED", None)
    assert close_kwargs["payload"] == {
        "from_state": "SETTLED",
        "to_state": "CLOSED",
    }
    assert close_kwargs["commit"] is False
