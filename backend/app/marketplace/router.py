from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.dependencies import current_user, require_farmer_kyc_verified, require_roles
from app.core.enums import Role
from app.db.session import get_db
from app.identity.models import User
from app.marketplace.models import Listing, MarketPriceRecommendation
from app.marketplace.schemas import (
    AdminMarketReferenceCreate,
    AdminMarketReferenceEdit,
    AdminMarketReferenceResponse,
    ListingContextResponse,
    ListingCreate,
    ListingResponse,
    ListingSearchResult,
    MarketRecommendationResponse,
)
from app.marketplace.service import (
    create_listing,
    create_market_reference,
    get_listing_context,
    version_market_reference,
)

router = APIRouter(prefix="/marketplace", tags=["marketplace"])


def _admin_reference_response(row: MarketPriceRecommendation, now: datetime) -> AdminMarketReferenceResponse:
    return AdminMarketReferenceResponse(
        recommendation_id=str(row.id),
        market_code=row.market_code,
        breed=row.breed,
        price_per_kg_paise=row.price_per_kg_paise,
        source_label=row.source_label,
        valid_from=row.valid_from,
        valid_to=row.valid_to,
        created_at=row.created_at,
        active=row.valid_from <= now and (row.valid_to is None or row.valid_to > now),
    )


@router.get("/listing-context", response_model=ListingContextResponse)
def listing_context(
    target_type: str = Query(..., pattern="^(GOAT|LOT)$"),
    target_id: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    user: User = Depends(require_farmer_kyc_verified),
):
    verified_weight, market_code = get_listing_context(db, user.id, target_type, target_id)
    return ListingContextResponse(
        target_type=target_type,
        target_id=target_id,
        verified_weight_kg=verified_weight,
        market_code=market_code,
    )


@router.get("/recommendations", response_model=list[MarketRecommendationResponse])
def recommendations(
    market_code: str = Query(...),
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    now = datetime.now(UTC)
    rows = db.scalars(
        select(MarketPriceRecommendation)
        .where(
            MarketPriceRecommendation.market_code == market_code.strip().upper(),
            MarketPriceRecommendation.valid_from <= now,
        )
        .order_by(MarketPriceRecommendation.valid_from.desc())
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


@router.get("/admin/references", response_model=list[AdminMarketReferenceResponse])
def admin_references(
    market_code: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(Role.ADMIN)),
):
    stmt = select(MarketPriceRecommendation)
    if market_code:
        stmt = stmt.where(MarketPriceRecommendation.market_code == market_code.strip().upper())
    rows = db.scalars(stmt.order_by(MarketPriceRecommendation.valid_from.desc())).all()
    now = datetime.now(UTC)
    return [_admin_reference_response(row, now) for row in rows]


@router.post("/admin/references", response_model=AdminMarketReferenceResponse, status_code=201)
def admin_create_reference(
    payload: AdminMarketReferenceCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(Role.ADMIN)),
):
    row = create_market_reference(
        db,
        payload.market_code,
        payload.breed,
        payload.price_per_kg_paise,
        payload.source_label,
        payload.valid_from,
        payload.valid_to,
    )
    return _admin_reference_response(row, datetime.now(UTC))


@router.put("/admin/references/{recommendation_id}", response_model=AdminMarketReferenceResponse)
def admin_edit_reference(
    recommendation_id: UUID,
    payload: AdminMarketReferenceEdit,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(Role.ADMIN)),
):
    row = version_market_reference(
        db,
        recommendation_id,
        payload.effective_from,
        payload.valid_to,
        payload.market_code,
        payload.breed,
        payload.price_per_kg_paise,
        payload.source_label,
    )
    return _admin_reference_response(row, datetime.now(UTC))


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
