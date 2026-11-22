import pytest
from streamlit.testing.v1 import AppTest

from data.target_repository import TargetRepository
from domain.units import cm_to_height, height_to_cm, kg_to_pounds, pounds_to_kg
from services.target_service import TargetService


def test_known_conversions_and_round_trip():
    assert pounds_to_kg(150) == pytest.approx(68.0388555)
    assert height_to_cm(5, 6) == pytest.approx(167.64)
    assert kg_to_pounds(pounds_to_kg(165.5)) == pytest.approx(165.5)
    feet, inches = cm_to_height(175)
    assert height_to_cm(feet, inches) == pytest.approx(175)


@pytest.mark.parametrize('goal', ['Lose', 'Maintain', 'Gain'])
def test_goal_and_measurements_survive_reopen(tmp_path, goal):
    path = tmp_path / 'test.db'
    service = TargetService(TargetRepository(path))
    service.calculate_and_save(pounds_to_kg(150), height_to_cm(5, 6), 27, 'Male', 'moderate', goal)
    restored = TargetRepository(path)
    record = restored.list_records()[0]
    assert record['goal'] == goal
    assert record['weight_kg'] == pytest.approx(68.0388555)
    assert record['height_cm'] == pytest.approx(167.64)
    assert restored.load()['calories'] == record['calories']


def test_empty_app_save_edit_and_delete(tmp_path, monkeypatch):
    original = TargetRepository.__init__
    monkeypatch.setattr(TargetRepository, '__init__', lambda self: original(self, tmp_path / 'ui.db'))
    app = AppTest.from_file('../app.py').run()
    assert not app.exception
    assert len(app.tabs) == 5
    app.button[0].click().run()
    assert not app.exception
    assert TargetRepository().list_records()[0]['goal'] == 'Lose'
    # Saving the edit should refresh immediately, with imperial values preserved.
    next(b for b in app.button if b.label == 'Save edited calculation').click().run()
    assert not app.exception
    assert kg_to_pounds(TargetRepository().list_records()[0]['weight_kg']) == pytest.approx(165)
    next(c for c in app.checkbox if 'cannot be undone' in c.label).check().run()
    next(b for b in app.button if b.label == 'Delete selected calculation').click().run()
    assert not app.exception
    assert TargetRepository().list_records() == []


def test_ui_displays_invalid_measurement_errors(tmp_path, monkeypatch):
    original = TargetRepository.__init__
    monkeypatch.setattr(TargetRepository, '__init__', lambda self: original(self, tmp_path / 'ui.db'))
    app = AppTest.from_file('../app.py').run()
    next(n for n in app.number_input if n.label == 'Weight (lb)').set_value(600)
    next(n for n in app.number_input if n.label == 'Height — feet').set_value(1)
    app.button[0].click().run()
    assert not app.exception
    assert '50 to 500 lb' in app.error[0].value
    assert TargetRepository().list_records() == []
    next(n for n in app.number_input if n.label == 'Weight (lb)').set_value(150)
    app.button[0].click().run()
    assert not app.exception
    assert '3 ft 0 in to 8 ft 0 in' in app.error[0].value
    assert TargetRepository().list_records() == []


@pytest.mark.parametrize('consumed, label', [(0, 'Remaining'), (3000, 'Above target')])
def test_today_dashboard_tracks_saved_intake(tmp_path, monkeypatch, consumed, label):
    from datetime import date

    original = TargetRepository.__init__
    monkeypatch.setattr(TargetRepository, '__init__', lambda self: original(self, tmp_path / 'ui.db'))
    repo = TargetRepository()
    TargetService(repo).calculate_and_save(75, 175, 30, 'Male', 'moderate', 'maintain')
    repo.save_log(date.today().isoformat(), 75, consumed)
    app = AppTest.from_file('../app.py').run()
    assert not app.exception
    assert next(m for m in app.metric if m.label == 'Logged today').value == f'{consumed:,} kcal'
    assert next(m for m in app.metric if m.label == label).value == f'{abs(2633-consumed):,} kcal'
