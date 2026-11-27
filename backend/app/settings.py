"""Settings of the backend, read from the environment (backend/.env.example lists them)."""

from __future__ import annotations

import math
import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

from app.auth.principal import Role

DEFAULT_DEV_USERS = "demo-teacher:teacher,demo-student:student,coteach-service:service"
DEVELOPMENT_AUTH_SECRET = "dev-only-secret-change-me-0123456789abcdef"
MIN_AUTH_SECRET_LENGTH = 32
"""Minimum HS256 secret length, as required by RFC 7518 §3.2."""
PRODUCTION_APP_ENV = "production"
INFERENCE_PIPELINES = ("models", "fake")


def _flag(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def _number(env: Mapping[str, str], name: str, default: float, *, zero: bool = False) -> float:
    """A finite number of the environment: positive, or also 0 when `zero` allows it."""
    raw = env.get(name)
    try:
        value = float(raw) if raw else default
    except ValueError:
        raise ValueError(f"{name} must be a number") from None
    if not math.isfinite(value) or value < 0 or (value == 0 and not zero):
        raise ValueError(f"{name} must be a finite number above 0{' or 0' if zero else ''}")
    return value


def _whole(env: Mapping[str, str], name: str, default: int, *, maximum: int | None = None) -> int:
    """A whole number of the environment above 0, and up to `maximum` when it has one."""
    raw = env.get(name)
    try:
        value = int(raw) if raw else default
    except ValueError:
        raise ValueError(f"{name} must be a whole number") from None
    if value <= 0:
        raise ValueError(f"{name} must be a whole number above 0")
    if maximum is not None and value > maximum:
        raise ValueError(f"{name} must be at most {maximum}")
    return value


def _dev_users(value: str) -> dict[str, Role]:
    users: dict[str, Role] = {}
    for entry in filter(None, (item.strip() for item in value.split(","))):
        subject, _, role = entry.partition(":")
        users[subject.strip()] = Role(role.strip())
    return users


@dataclass(frozen=True)
class Settings:
    app_env: str = "development"
    """Runtime environment. Production enables startup validation for authentication secrets."""
    database_url: str | None = None
    """SQLAlchemy URL of PostgreSQL. Without it, /ready reports the database as unavailable."""
    auth_secret: str | None = None
    """Key of the tokens (HS256, 32+ characters). Without a valid one, /v1 always answers 401."""
    auth_audience: str = "coteach-ai-api"
    auth_issuer: str = "coteach-ai-dev-issuer"
    auth_dev_issuer: bool = False
    """Exposes POST /dev/token. Only for development and local demos (spec api-access)."""
    auth_dev_token_ttl_seconds: int = 3600
    auth_dev_users: Mapping[str, Role] = field(
        default_factory=lambda: _dev_users(DEFAULT_DEV_USERS)
    )
    frontend_origin: str | None = None
    """Only origin allowed by CORS. Without it, no cross-origin request is allowed."""
    review_period_hours: float = 24
    """Time the teacher has to review a result before it is published (PRD DEC-05, provisional)."""
    inference_pipeline: str = "models"
    """Pipeline of the worker: `models` (real adapters) or `fake` (synthetic result, no models)."""
    fake_stage_seconds: float = 2
    """Wait of FakePipeline in each stage, to see the progress in the web."""
    worker_poll_seconds: float = 1
    """Wait of the worker when the queue is empty or the database is not available."""
    max_attempts: int = 3
    """Attempts of a job with transient failures before it moves to `failed` (RNF-05)."""
    retry_delay_seconds: float = 60
    """Wait before the second attempt; it doubles before each later one."""
    maintenance_interval_seconds: float = 60
    """Time between two maintenance cycles."""
    upload_max_bytes: int = 150 * 1024 * 1024
    """Largest audio accepted by POST /v1/classes (413 audio_too_large above it)."""
    upload_min_seconds: float = 60
    """Shortest audio accepted (422 invalid_audio_duration below it)."""
    upload_max_seconds: float = 2 * 60 * 60
    """Longest audio accepted (422 invalid_audio_duration above it)."""
    audio_retention_days: float = 14
    """Days the original audio is kept before maintenance purges it (RNF-02, ADR-0004)."""
    audio_storage_dir: str = "data/audio"
    """Private directory of the audio, outside Git. Relative to the working directory."""
    work_dir: str = "data/work"
    """Private work copies of each attempt, outside AUDIO_STORAGE_DIR and Git."""
    models_dir: str = "data/models"
    """Private cache of the fixed model revisions, outside Git and backups."""
    hf_token: str | None = field(default=None, repr=False)
    """Token to download gated models. Only needed by `make models`, never by the worker."""
    asr_model: str = "small"
    """Whisper size for faster-whisper (ADR-0003: small, multilingual)."""
    asr_device: str = "cpu"
    """Device of the transcription model; CPU is the default of the local demo."""
    asr_compute_type: str = "int8"
    """Quantization of the transcription model on CPU."""
    asr_language: str = ""
    """Forced language; empty detects it per phrase."""

    def __post_init__(self) -> None:
        if self.app_env == PRODUCTION_APP_ENV:
            self._validate_production_auth_secret()
        if self.upload_min_seconds > self.upload_max_seconds:
            raise ValueError("UPLOAD_MIN_SECONDS cannot be above UPLOAD_MAX_SECONDS")
        work = Path(self.work_dir).resolve()
        audio = Path(self.audio_storage_dir).resolve()
        if work == audio or work.is_relative_to(audio) or audio.is_relative_to(work):
            raise ValueError("WORK_DIR must be outside AUDIO_STORAGE_DIR")
        if self.inference_pipeline not in INFERENCE_PIPELINES:
            raise ValueError("INFERENCE_PIPELINE must be 'models' or 'fake'")
        if self.asr_model != "small":
            raise ValueError("ASR_MODEL only supports 'small'")

    def _validate_production_auth_secret(self) -> None:
        secret = self.auth_secret
        if (
            not secret
            or not secret.strip()
            or len(secret) < MIN_AUTH_SECRET_LENGTH
            or secret == DEVELOPMENT_AUTH_SECRET
        ):
            raise ValueError(
                "AUTH_SECRET must be a non-development secret with at least 32 characters "
                "when APP_ENV=production"
            )

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> Settings:
        env = os.environ if env is None else env
        defaults = cls()
        return cls(
            app_env=env.get("APP_ENV") or defaults.app_env,
            database_url=env.get("DATABASE_URL") or None,
            auth_secret=env.get("AUTH_SECRET") or None,
            auth_audience=env.get("AUTH_AUDIENCE") or defaults.auth_audience,
            auth_issuer=env.get("AUTH_ISSUER") or defaults.auth_issuer,
            auth_dev_issuer=_flag(env.get("AUTH_DEV_ISSUER")),
            auth_dev_token_ttl_seconds=int(
                env.get("AUTH_DEV_TOKEN_TTL_SECONDS") or defaults.auth_dev_token_ttl_seconds
            ),
            auth_dev_users=_dev_users(env.get("AUTH_DEV_USERS") or DEFAULT_DEV_USERS),
            frontend_origin=env.get("FRONTEND_ORIGIN") or None,
            review_period_hours=_number(env, "REVIEW_PERIOD_HOURS", defaults.review_period_hours),
            inference_pipeline=(env.get("INFERENCE_PIPELINE") or defaults.inference_pipeline)
            .strip()
            .lower(),
            fake_stage_seconds=_number(
                env, "FAKE_STAGE_SECONDS", defaults.fake_stage_seconds, zero=True
            ),
            worker_poll_seconds=_number(env, "WORKER_POLL_SECONDS", defaults.worker_poll_seconds),
            max_attempts=_whole(env, "MAX_ATTEMPTS", defaults.max_attempts, maximum=20),
            retry_delay_seconds=_number(
                env, "RETRY_DELAY_SECONDS", defaults.retry_delay_seconds, zero=True
            ),
            maintenance_interval_seconds=_number(
                env, "MAINTENANCE_INTERVAL_SECONDS", defaults.maintenance_interval_seconds
            ),
            upload_max_bytes=_whole(env, "UPLOAD_MAX_BYTES", defaults.upload_max_bytes),
            upload_min_seconds=_number(
                env, "UPLOAD_MIN_SECONDS", defaults.upload_min_seconds, zero=True
            ),
            upload_max_seconds=_number(env, "UPLOAD_MAX_SECONDS", defaults.upload_max_seconds),
            audio_retention_days=_number(
                env, "AUDIO_RETENTION_DAYS", defaults.audio_retention_days
            ),
            audio_storage_dir=env.get("AUDIO_STORAGE_DIR") or defaults.audio_storage_dir,
            work_dir=env.get("WORK_DIR") or defaults.work_dir,
            models_dir=env.get("MODELS_DIR") or defaults.models_dir,
            hf_token=env.get("HF_TOKEN") or None,
            asr_model=env.get("ASR_MODEL") or defaults.asr_model,
            asr_device=env.get("ASR_DEVICE") or defaults.asr_device,
            asr_compute_type=env.get("ASR_COMPUTE_TYPE") or defaults.asr_compute_type,
            asr_language=env.get("ASR_LANGUAGE") or defaults.asr_language,
        )
