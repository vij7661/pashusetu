from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import current_user, require_farmer_kyc_verified
from app.db.session import get_db
from app.identity.models import User
from app.marketplace.models import Listing, MarketPriceRecommendation
from app.marketplace.schemas import (
    ListingCreate,
    ListingEligibilityResponse,
    ListingResponse,
    ListingSearchResult,
    MarketRecommendationResponse,
)
from app.marketplace.service import (
    create_listing,
    farmer_listings,
    listing_eligibility,
    target_code_for_listing,
)

router = APIRouter(prefix="/marketplace", tags=["marketplace"])


@router.get("/recommendations", response_model=list[MarketRecommendationResponse])
def recommendations(
    market_code: str = Query(...),
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    now = datetime.now(UTC)
    rows = db.scalars(
        select(MarketPriceRecommendation).where(
            MarketPriceRecommendation.market_code == market_code,
            MarketPriceRecommendation.valid_from <= now,
        )
    ).all()
    return [
        MarketRecommendationResponse(
            recommendation_id=str(x.id),
            market_code=x.market_code,
            breed=x.breed,
            price_per_kg_paise=x.price_per_kg_paise,
            source_label=x.source_label,
        )
        for x in rows
        if x.valid_to is None or x.valid_to > now
    ]


@router.get("/listings/eligibility", response_model=ListingEligibilityResponse)
def get_listing_eligibility(
    target_type: str = Query(pattern="^(GOAT|LOT)$"),
    target_id: str = Query(min_length=1),
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    _, session, verified_weight = listing_eligibility(
        db,
        user.id,
        target_type,
        target_id,
    )
    return ListingEligibilityResponse(
        target_type=target_type,
        target_id=target_id,
        weighment_id=session.weighment_code,
        verified_weight_kg=verified_weight,
    )


@router.get("/farmers/me/listings", response_model=list[ListingResponse])
def get_farmer_listings(
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    rows = farmer_listings(db, user.id)
    return [
        ListingResponse(
            listing_id=x.listing_code,
            target_type=x.target_type,
            target_id=target_code_for_listing(db, x),
            verified_weight_kg=x.verified_weight_kg,
            farmer_price_per_kg_paise=x.farmer_price_per_kg_paise,
            farmer_total_value_paise=x.farmer_total_value_paise,
            sale_type=x.sale_type,
            opens_at=x.opens_at,
            closes_at=x.closes_at,
            status=x.status,
        )
        for x in rows
    ]


@router.post("/listings", response_model=ListingResponse, status_code=201)
def post_listing(
    payload: ListingCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_farmer_kyc_verified),
):
    listing = create_listing(
        db,
        user.id,
        payload.target_type,
        payload.target_id,
        payload.farmer_price_per_kg_paise,
        payload.sale_type,
        payload.opens_at,
        payload.closes_at,
        UUID(payload.recommendation_id) if payload.recommendation_id else None,
    )
    return ListingResponse(
        listing_id=listing.listing_code,
        target_type=listing.target_type,
        target_id=payload.target_id,
        verified_weight_kg=listing.verified_weight_kg,
        farmer_price_per_kg_paise=listing.farmer_price_per_kg_paise,
        farmer_total_value_paise=listing.farmer_total_value_paise,
        sale_type=listing.sale_type,
        opens_at=listing.opens_at,
        closes_at=listing.closes_at,
        status=listing.status,
    )


@router.get("/listings", response_model=list[ListingSearchResult])
def search_listings(
    min_weight_kg: float | None = None,
    max_weight_kg: float | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    stmt = select(Listing).where(Listing.status == "PUBLISHED")
    if min_weight_kg is not None:
        stmt = stmt.where(Listing.verified_weight_kg >= min_weight_kg)
    if max_weight_kg is not None:
        stmt = stmt.where(Listing.verified_weight_kg <= max_weight_kg)
    rows = db.scalars(stmt.order_by(Listing.created_at.desc())).all()
    return [
        ListingSearchResult(
            listing_id=x.listing_code,
            target_type=x.target_type,
            verified_weight_kg=x.verified_weight_kg,
            farmer_price_per_kg_paise=x.farmer_price_per_kg_paise,
            farmer_total_value_paise=x.farmer_total_value_paise,
            status=x.status,
        )
        for x in rows
    ]
