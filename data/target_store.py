"""Persistence contract for nutrition targets, independent of SQLite."""

from typing import Any, Protocol


class TargetStore(Protocol):
    def save(self, targets: dict[str, int], inputs: dict[str, Any] | None = None) -> int | None:
        """Append a calculation."""
        ...

    def load(self) -> dict[str, int] | None:
        """Read the most recent target values."""
        ...

    def list_records(self) -> list[dict]:
        """Read historical calculations."""
        ...

    def get_record(self, record_id: int) -> dict | None:
        """Read one calculation."""
        ...

    def update_record(self, record_id: int, inputs: dict, targets: dict) -> bool:
        """Edit a calculation."""
        ...

    def delete_record(self, record_id: int) -> bool:
        """Delete a calculation."""
        ...
