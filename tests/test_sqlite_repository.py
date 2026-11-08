"""Verify SQLite-backed history survives new repository instances and supports CRUD."""

from data.target_repository import TargetRepository
from services.target_service import TargetService

INPUTS = dict(weight_kg=75, height_cm=175, age=30, sex="male",
              activity_level="moderate", goal="maintain")


def test_history_persists_and_latest_result_is_loaded(tmp_path):
    db_path = tmp_path / "nutrition.db"
    service = TargetService(TargetRepository(db_path))
    first = service.calculate_and_save(**INPUTS)
    service.calculate_and_save(**{**INPUTS, "goal": "lose"})
    restored = TargetRepository(db_path)
    records = restored.list_records()
    assert len(records) == 2
    assert [record["goal"] for record in records] == ["lose", "maintain"]
    assert restored.load()["calories"] == first["calories"] - 500
    assert records[0]["weight_kg"] == 75


def test_edit_recalculates_and_delete_removes_record(tmp_path):
    service = TargetService(TargetRepository(tmp_path / "nutrition.db"))
    service.calculate_and_save(**INPUTS)
    record_id = service.list_calculations()[0]["id"]
    assert service.edit_calculation(record_id, **{**INPUTS, "goal": "gain"})
    assert service.get_calculation(record_id)["calories"] == 3133
    assert not service.edit_calculation(99999, **INPUTS)
    assert service.delete_calculation(record_id)
    assert service.list_calculations() == []
    assert service.get_saved_targets() is None
    assert not service.delete_calculation(record_id)


def test_log_upsert_and_delete(tmp_path):
    repo = TargetRepository(tmp_path / "nutrition.db")
    repo.save_log("2026-11-07", 75.0, 2200)
    repo.save_log("2026-11-07", 74.5, 2100)
    repo.save_log("2026-11-08", 74.3, 2050)
    assert len(repo.list_logs()) == 2
    assert repo.list_logs("2026-11-08", "2026-11-08")[0]["weight_kg"] == 74.3
    assert repo.delete_log("2026-11-07")
    assert len(repo.list_logs()) == 1
