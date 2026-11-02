"""Abstraction for persistence of calculated nutrition targets."""

from typing import Protocol


class TargetStore(Protocol):
    """Storage contract used by the service, independent of JSON files."""

    def save(self, targets: dict[str, int]) -> None:
        """Persist the latest nutrition targets."""
        ...

    def load(self) -> dict[str, int] | None:
        """Return the latest targets, or None when no data exists."""
        ...
