import pytest
from app.core.errors import AppError
from app.transaction.state_machine import assert_transition


def test_offer_accepted_to_agreement_pending():
    assert_transition("OFFER_ACCEPTED", "AGREEMENT_PENDING")


def test_agreement_pending_to_locked():
    assert_transition("AGREEMENT_PENDING", "AGREEMENT_LOCKED")


def test_invalid_jump_is_blocked():
    with pytest.raises(AppError):
        assert_transition("OFFER_ACCEPTED", "FUNDS_SECURED")
