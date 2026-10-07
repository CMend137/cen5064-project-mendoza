from data.target_repository import TargetRepository
from domain.target_calculator import calculate_targets


class TargetService:
    """Coordinates target calculations and persistence."""

    def __init__(self, repository=None):
        self.repository = repository or TargetRepository()

    def calculate_and_save(
        self,
        weight_kg,
        height_cm,
        age,
        sex,
        activity_level,
        goal,
    ):
        targets = calculate_targets(
            weight_kg=weight_kg,
            height_cm=height_cm,
            age=age,
            sex=sex,
            activity_level=activity_level,
            goal=goal,
        )

        self.repository.save(targets)

        return self.repository.load()

    def get_saved_targets(self):
        return self.repository.load()