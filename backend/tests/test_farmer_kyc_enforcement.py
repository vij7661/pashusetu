import inspect
from pathlib import Path

from app.agreement.router import post_agreement, post_confirm
from app.auth.dependencies import require_farmer_kyc_verified
from app.bidding.router import post_accept_bid
from app.disputes.router import (
    post_dispute,
    post_evidence,
    post_resolve,
    post_reweigh,
)
from app.logistics.router import assign_transport, delivery, pickup
from app.marketplace.router import post_listing
from app.payments.router import secure, settle_transaction
from app.transaction.router import close_transaction, create_from_listing

TRANSACTIONAL_FARMER_MUTATIONS = (
    post_listing,
    post_accept_bid,
    create_from_listing,
    close_transaction,
    post_agreement,
    post_confirm,
    secure,
    settle_transaction,
    post_dispute,
    post_evidence,
    post_reweigh,
    post_resolve,
    assign_transport,
    pickup,
    delivery,
)


def test_all_farmer_transactional_mutations_require_verified_kyc():
    for endpoint in TRANSACTIONAL_FARMER_MUTATIONS:
        user_parameter = inspect.signature(endpoint).parameters["user"]
        dependency = user_parameter.default.dependency
        assert dependency is require_farmer_kyc_verified, endpoint.__name__


def test_farmer_registration_migration_normalizes_legacy_kyc_statuses():
    migration = (
        Path(__file__).parents[1]
        / "migrations"
        / "versions"
        / "0008_farmer_registration_lifecycle.py"
    ).read_text(encoding="utf-8")

    assert "SET kyc_status = 'KYC_VERIFIED' WHERE kyc_status = 'VERIFIED'" in migration
    assert "SET kyc_status = 'KYC_PENDING' WHERE kyc_status = 'PENDING'" in migration
    assert "SET kyc_status = 'VERIFIED' WHERE kyc_status = 'KYC_VERIFIED'" in migration
    assert "SET kyc_status = 'PENDING' WHERE kyc_status = 'KYC_PENDING'" in migration
