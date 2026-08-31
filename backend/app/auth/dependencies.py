from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import Role
from app.core.errors import AppError
from app.core.permissions import role_has_permission
from app.core.security import decode_token
from app.db.session import get_db
from app.identity.models import User
from app.identity.profile_models import FarmerProfile, FarmerRegistration

bearer = HTTPBearer(auto_error=False)


def _claims(creds: HTTPAuthorizationCredentials | None) -> dict:
    if creds is None:
        raise AppError("AUTH_REQUIRED", "Authentication required.", 401)
    try:
        return decode_token(creds.credentials)
    except Exception as exc:
        raise AppError("TOKEN_INVALID", "Invalid or expired token.", 401) from exc


def current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    claims = _claims(creds)
    if claims.get("type") != "access":
        raise AppError("TOKEN_INVALID", "Access token required.", 401)
    try:
        user_id = UUID(claims["sub"])
    except (KeyError, ValueError) as exc:
        raise AppError("TOKEN_INVALID", "Invalid access token subject.", 401) from exc
    user = db.get(User, user_id)
    if user is None:
        raise AppError("USER_NOT_FOUND", "User not found.", 401)
    if user.status != "ACTIVE":
        raise AppError("USER_INACTIVE", "User account is not active.", 403)
    return user


def current_farmer_registration(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> FarmerRegistration:
    claims = _claims(creds)
    if claims.get("type") != "farmer_registration":
        raise AppError("TOKEN_INVALID", "Farmer registration token required.", 401)
    try:
        registration_id = UUID(claims["sub"])
    except (KeyError, ValueError) as exc:
        raise AppError("TOKEN_INVALID", "Invalid registration token subject.", 401) from exc
    registration = db.get(FarmerRegistration, registration_id)
    if registration is None:
        raise AppError("REGISTRATION_NOT_FOUND", "Farmer registration not found.", 404)
    return registration


def require_farmer_kyc_verified(
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> User:
    farmer_role = any(role.role == Role.FARMER.value for role in user.roles)
    if not farmer_role:
        return user
    profile = db.scalar(select(FarmerProfile).where(FarmerProfile.user_id == user.id))
    if profile is None:
        raise AppError("FARMER_PROFILE_NOT_FOUND", "Farmer profile not found.", 403)
    if profile.kyc_status != "KYC_VERIFIED":
        raise AppError(
            "KYC_VERIFICATION_REQUIRED",
            "KYC verification is required before transactional actions.",
            403,
        )
    return user


def require_roles(*allowed: Role):
    allowed_values = {r.value for r in allowed}

    def dependency(
        creds: HTTPAuthorizationCredentials | None = Depends(bearer),
        db: Session = Depends(get_db),
    ) -> User:
        user = current_user(creds, db)
        roles = {r.role for r in user.roles}
        if roles.isdisjoint(allowed_values):
            raise AppError("FORBIDDEN", "Insufficient permission.", 403)
        return user

    return dependency


def require_permission(permission: str):
    def dependency(
        user: User = Depends(current_user),
    ) -> User:
        roles = [r.role for r in user.roles]
        if not any(role_has_permission(role, permission) for role in roles):
            raise AppError("FORBIDDEN", f"Missing permission: {permission}", 403)
        return user

    return dependency
