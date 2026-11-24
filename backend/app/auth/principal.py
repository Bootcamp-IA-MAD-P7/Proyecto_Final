"""Who is calling: the subject and the role of a validated token (ADR-0004)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Role(StrEnum):
    TEACHER = "teacher"
    STUDENT = "student"
    SERVICE = "service"
    """CoTeach service credential: submits classes on behalf of a teacher."""


@dataclass(frozen=True)
class Principal:
    subject: str
    role: Role
