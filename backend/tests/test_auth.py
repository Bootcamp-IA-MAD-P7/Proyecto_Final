"""Signed tokens and the isolated test issuer POST /dev/token (spec api-access)."""

from dataclasses import replace

import pytest
from fastapi.testclient import TestClient

from app.auth.principal import Principal, Role
from app.auth.tokens import InvalidTokenError, issue_token, verify_token
from app.main import create_app
from app.settings import Settings
from tests.conftest import SETTINGS

DEV = replace(SETTINGS, auth_dev_issuer=True)


def test_token_round_trip():
    principal = Principal("demo-teacher", Role.TEACHER)

    assert verify_token(SETTINGS, issue_token(SETTINGS, principal)) == principal


def test_token_with_an_unknown_role_is_rejected():
    import jwt

    claims = {"sub": "x", "role": "admin", "aud": SETTINGS.auth_audience, "exp": 4102444800}
    forged = jwt.encode({**claims, "iss": SETTINGS.auth_issuer}, SETTINGS.auth_secret)

    with pytest.raises(InvalidTokenError):
        verify_token(SETTINGS, forged)


def test_dev_issuer_is_off_by_default(store):
    client = TestClient(create_app(SETTINGS, store=store))

    response = client.post("/dev/token", json={"user": "demo-teacher"})

    assert response.status_code == 404
    assert "access_token" not in response.text


@pytest.mark.parametrize(
    ("user", "role"),
    [("demo-teacher", "teacher"), ("demo-student", "student"), ("coteach-service", "service")],
)
def test_dev_issuer_signs_tokens_for_synthetic_users(store, user, role):
    client = TestClient(create_app(DEV, store=store))

    body = client.post("/dev/token", json={"user": user}).json()

    assert (body["subject"], body["role"], body["token_type"]) == (user, role, "bearer")
    assert verify_token(DEV, body["access_token"]) == Principal(user, Role(role))
    headers = {"Authorization": f"Bearer {body['access_token']}"}
    assert client.get("/v1/jobs/job-x", headers=headers).status_code == 404


def test_dev_issuer_refuses_unknown_users(store):
    client = TestClient(create_app(DEV, store=store))

    response = client.post("/dev/token", json={"user": "someone-else"})

    assert response.status_code == 404
    assert "access_token" not in response.text


def test_dev_issuer_is_not_in_the_contract():
    assert "/dev/token" not in create_app(DEV).openapi()["paths"]


def test_settings_from_env():
    settings = Settings.from_env(
        {
            "DATABASE_URL": "postgresql+psycopg://u:p@db/x",
            "AUTH_SECRET": "s",
            "AUTH_DEV_ISSUER": "true",
            "AUTH_DEV_USERS": "a:teacher, b:student",
            "FRONTEND_ORIGIN": "http://localhost:5173",
        }
    )

    assert settings.auth_dev_issuer is True
    assert dict(settings.auth_dev_users) == {"a": Role.TEACHER, "b": Role.STUDENT}
    assert Settings.from_env({}).auth_dev_issuer is False
