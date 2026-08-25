from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.enums import Role
from app.core.errors import AppError
from app.core.permissions import role_has_permission
from app.core.security import decode_token
from app.db.session import get_db
from app.identity.models import User

bearer = HTTPBearer(auto_error=False)


def current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    if creds is None:
        raise AppError("AUTH_REQUIRED", "Authentication required.", 401)
    try:
        claims = decode_token(creds.credentials)
    except Exception as exc:
        raise AppError("TOKEN_INVALID", "Invalid or expired access token.", 401) from exc
    if claims.get("type") != "access":
        raise AppError("TOKEN_INVALID", "Access token required.", 401)
    user = db.get(User, UUID(claims["sub"]))
    if user is None:
        raise AppError("USER_NOT_FOUND", "User not found.", 401)
    if user.status != "ACTIVE":
        raise AppError("USER_INACTIVE", "User account is not active.", 403)
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
