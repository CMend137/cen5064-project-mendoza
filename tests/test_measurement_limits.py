import pytest

from data.target_repository import TargetRepository
from domain.units import height_to_cm, pounds_to_kg
from domain.validation import validate_measurements
from services.progress_service import ProgressService
from services.target_service import TargetService

VALID = {'weight_kg': 75, 'height_cm': 175, 'age': 30, 'sex': 'male', 'activity_level': 'moderate', 'goal': 'maintain'}


@pytest.mark.parametrize('field,value', [
    ('weight_kg', pounds_to_kg(49.9)), ('weight_kg', pounds_to_kg(500.1)),
    ('height_cm', height_to_cm(1, 0)), ('height_cm', height_to_cm(8, 0.1)),
    ('age', 17), ('age', 101), ('age', 25.5),
    ('weight_kg', float('nan')), ('height_cm', float('inf')), ('age', float('nan')),
])
def test_invalid_create_and_edit_leave_database_unchanged(tmp_path, field, value):
    service = TargetService(TargetRepository(tmp_path / 'test.db'))
    service.calculate_and_save(**VALID)
    before = service.list_calculations()
    invalid = {**VALID, field: value}
    with pytest.raises(ValueError):
        service.calculate_and_save(**invalid)
    with pytest.raises(ValueError):
        service.edit_calculation(before[0]['id'], **invalid)
    assert service.list_calculations() == before


@pytest.mark.parametrize('lb,feet,age', [(50, 3, 18), (500, 8, 100)])
def test_supported_boundaries(lb, feet, age):
    validate_measurements(pounds_to_kg(lb), height_to_cm(feet, 0), age)


@pytest.mark.parametrize('lb', [49, 600, float('inf'), float('nan')])
def test_daily_log_rejects_invalid_weight_without_overwriting(tmp_path, lb):
    repo = TargetRepository(tmp_path / 'test.db')
    service = ProgressService(repo)
    service.save_daily_log('2026-11-16', 75, 2000)
    before = repo.list_logs()
    with pytest.raises(ValueError):
        service.save_daily_log('2026-11-16', pounds_to_kg(lb), 2000)
    assert repo.list_logs() == before
