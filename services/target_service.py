"""Application use cases for nutrition target calculations and history."""

from data.target_store import TargetStore
from domain.target_calculator import calculate_targets


class TargetService:
    def __init__(self, repository: TargetStore):
        self.repository = repository

    def calculate_and_save(self, weight_kg, height_cm, age, sex, activity_level, goal):
        inputs = dict(
            weight_kg=weight_kg,
            height_cm=height_cm,
            age=age,
            sex=sex,
            activity_level=activity_level,
            goal=goal,
        )
        targets = calculate_targets(**inputs)
        self.repository.save(targets, inputs=inputs)
        return self.repository.load()

    def get_saved_targets(self):
        return self.repository.load()

    def list_calculations(self):
        return self.repository.list_records()

    def get_calculation(self, record_id):
        return self.repository.get_record(record_id)

    def edit_calculation(self, record_id, **inputs):
        targets = calculate_targets(**inputs)
        return self.repository.update_record(record_id, inputs, targets)

    def delete_calculation(self, record_id):
        return self.repository.delete_record(record_id)
