from types import SimpleNamespace

from pydantic import ValidationError
import pytest

from app.weighment.schemas import AcknowledgeResponse
from app.weighment.service import acknowledge_weighment


class FakeDb:
    def __init__(self):
        self.commit_count = 0

    def commit(self):
        self.commit_count += 1


def test_farmer_rejection_is_a_domain_outcome_that_enables_reweigh():
    db = FakeDb()
    session = SimpleNamespace(status="FARMER_REVIEW")

    acknowledgement = acknowledge_weighment(
        db,
        session,
        acknowledged=False,
        method="APP_CONFIRMATION",
    )

    assert acknowledgement is None
    assert session.status == "REJECTED_BY_FARMER"
    assert db.commit_count == 1


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
