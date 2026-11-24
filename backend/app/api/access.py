"""Access to a class, resolved on the server from the token and the participants (ADR-0004)."""

from __future__ import annotations

from app.auth.principal import Principal, Role
from app.contract import ParticipantRole
from app.jobs import StoredClass

SUBMITTER_ROLES = frozenset({Role.TEACHER, Role.SERVICE})


def can_submit(principal: Principal) -> bool:
    return principal.role in SUBMITTER_ROLES


def can_see(principal: Principal, stored: StoredClass) -> bool:
    """Who submitted the class, or a participant whose participant_id is the token subject."""
    return principal.subject == stored.submitted_by or any(
        participant.participant_id == principal.subject
        for participant in stored.metadata.participants
    )


def teaches(principal: Principal, stored: StoredClass) -> bool:
    """Sees the draft and may review and approve: the submitter, or a teacher of the class.

    Being a teacher needs both the teacher role in the token and in the participants list:
    the role sent in the metadata never grants permissions on its own.
    """
    if principal.subject == stored.submitted_by:
        return True
    return principal.role == Role.TEACHER and any(
        participant.participant_id == principal.subject
        and participant.role == ParticipantRole.TEACHER
        for participant in stored.metadata.participants
    )
