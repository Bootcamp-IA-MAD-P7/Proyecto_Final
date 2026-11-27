"""Model-free adapters used until the real ones arrive in sections 2 and 3."""

from __future__ import annotations

from app.contract import Analysis, Transcript


class EmptyAnalyzer:
    """No pedagogical analysis until E4: keep the stage, emit an empty result."""

    def load(self) -> None:
        return None

    def close(self) -> None:
        return None

    def analyze(self, transcript: Transcript) -> Analysis:
        return Analysis(general_summary="", items=[])
