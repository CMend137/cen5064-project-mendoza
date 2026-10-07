import json
from pathlib import Path


class TargetRepository:
    """Handles saving and loading calculated nutrition targets."""

    def __init__(self, file_path="data/targets.json"):
        self.file_path = Path(file_path)

    def save(self, targets):
        """Save the latest calculated targets to a JSON file."""
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        with self.file_path.open("w", encoding="utf-8") as file:
            json.dump(targets, file, indent=4)

    def load(self):
        """Load the most recently saved targets."""
        if not self.file_path.exists():
            return None

        with self.file_path.open("r", encoding="utf-8") as file:
            return json.load(file)