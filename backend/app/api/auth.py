"""Authentication of /v1 and the isolated test issuer POST /dev/token (spec api-access)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.security.utils import get_authorization_scheme_param
from pydantic import BaseModel, ConfigDict

from app.api.errors import ApiError
from app.auth.principal import Principal
from app.auth.tokens import InvalidTokenError, issue_token, verify_token
from app.contract import ErrorCode, Identifier
from app.settings import Settings

bearer = HTTPBearer(
    auto_error=False,
    scheme_name="bearerToken",
    description="Signed token of the identity issuer. The role comes from it, never from the body.",
)


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_principal(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> Principal:
    if credentials is None:
        raise ApiError(401, ErrorCode.UNAUTHENTICATED)
    try:
        return verify_token(get_settings(request), credentials.credentials)
    except InvalidTokenError as error:
        raise ApiError(401, ErrorCode.UNAUTHENTICATED) from error


def principal_from_authorization(settings: Settings, authorization: str | None) -> Principal:
    """Authenticate an Authorization header before a large multipart body is read."""
    scheme, token = get_authorization_scheme_param(authorization)
    if scheme.lower() != "bearer" or not token:
        raise ApiError(401, ErrorCode.UNAUTHENTICATED)
    try:
        return verify_token(settings, token)
    except InvalidTokenError as error:
        raise ApiError(401, ErrorCode.UNAUTHENTICATED) from error


CurrentPrincipal = Annotated[Principal, Depends(get_principal)]


class DevTokenRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user: Identifier
    """One of the synthetic users of AUTH_DEV_USERS."""


class DevToken(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    subject: str
    role: str


dev_router = APIRouter(prefix="/dev", tags=["dev"], include_in_schema=False)
"""Not part of the contract: mounted only with AUTH_DEV_ISSUER=true (PRD §14)."""


@dev_router.post("/token", response_model=DevToken)
def issue_dev_token(request: Request, body: DevTokenRequest) -> DevToken:
    settings = get_settings(request)
    role = settings.auth_dev_users.get(body.user)
    if role is None:
        raise ApiError(404, ErrorCode.RESOURCE_NOT_AVAILABLE)
    principal = Principal(subject=body.user, role=role)
    try:
        access_token = issue_token(settings, principal)
    except InvalidTokenError as error:
        raise ApiError(404, ErrorCode.RESOURCE_NOT_AVAILABLE) from error
    return DevToken(
        access_token=access_token,
        expires_in=settings.auth_dev_token_ttl_seconds,
        subject=principal.subject,
        role=principal.role.value,
    )
