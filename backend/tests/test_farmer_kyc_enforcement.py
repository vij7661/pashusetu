import inspect

from app.agreement.router import post_agreement, post_confirm
from app.auth.dependencies import require_farmer_kyc_verified
from app.bidding.router import post_accept_bid
from app.disputes.router import (
    platform_resolver_required,
    post_dispute,
    post_evidence,
    post_resolve,
    post_reweigh,
)
from app.logistics.router import assign_transport, delivery, pickup
from app.marketplace.router import post_listing
from app.payments.router import secure, settle_transaction
from app.transaction.router import create_from_listing
from app.transaction.router import router as transaction_router

TRANSACTIONAL_FARMER_MUTATIONS = (
    post_listing,
    post_accept_bid,
    create_from_listing,
    post_agreement,
    post_confirm,
    secure,
    settle_transaction,
    post_dispute,
    post_evidence,
    post_reweigh,
    assign_transport,
    pickup,
    delivery,
)


def test_all_farmer_transactional_mutations_require_verified_kyc():
    for endpoint in TRANSACTIONAL_FARMER_MUTATIONS:
        user_parameter = inspect.signature(endpoint).parameters["user"]
        dependency = user_parameter.default.dependency
        assert dependency is require_farmer_kyc_verified, endpoint.__name__


def test_dispute_resolution_is_platform_controlled():
    user_parameter = inspect.signature(post_resolve).parameters["user"]
    assert user_parameter.default.dependency is platform_resolver_required


def test_transaction_close_is_not_a_party_facing_mutation():
    party_close_routes = [
        route
        for route in transaction_router.routes
        if route.path == "/transaction/{transaction_id}/close"
        and "POST" in route.methods
    ]
    assert party_close_routes == []
