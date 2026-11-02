"""Test Dependency Inversion with interchangeable target stores."""

from data.target_repository import TargetRepository
from services.target_service import TargetService


class InMemoryTargetStore:
    """A test double with the same save/load contract as the JSON store."""

    def __init__(self):
        self.targets = None

    def save(self, targets):
        self.targets = targets.copy()

    def load(self):
        return None if self.targets is None else self.targets.copy()


def test_service_calculates_and_saves_with_in_memory_store():
    store = InMemoryTargetStore()
    service = TargetService(repository=store)

    result = service.calculate_and_save(
        weight_kg=75,
        height_cm=175,
        age=30,
        sex="male",
        activity_level="moderate",
        goal="maintain",
    )

    assert result == {
        "calories": 2633,
        "protein": 150,
        "fat": 73,
        "carbohydrates": 344,
    }
    assert store.load() == result
    assert service.get_saved_targets() == result


def test_service_loads_no_targets_from_empty_store():
    service = TargetService(repository=InMemoryTargetStore())
    assert service.get_saved_targets() is None


def test_service_still_works_with_json_store(tmp_path):
    store = TargetRepository(file_path=tmp_path / "targets.json")
    service = TargetService(repository=store)

    result = service.calculate_and_save(
        weight_kg=75,
        height_cm=175,
        age=30,
        sex="male",
        activity_level="moderate",
        goal="maintain",
    )

    assert store.file_path.exists()
    assert service.get_saved_targets() == result
