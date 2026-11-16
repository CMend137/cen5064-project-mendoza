"""Exercise history actions through Streamlit with an isolated database."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import data.target_repository as repository_module
from services.target_service import TargetService


@pytest.fixture
def history_app(tmp_path, monkeypatch):
    repository = repository_module.TargetRepository(tmp_path / "test.db")
    monkeypatch.setattr(repository_module, "TargetRepository", lambda: repository)
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"))
    return app, repository


def button(app, label):
    return next(item for item in app.button if item.label == label)


def test_empty_history_still_renders_other_tabs(history_app):
    app, _ = history_app
    app.run(timeout=10)
    assert not app.exception
    assert any(item.label == "Save daily entry" for item in app.button)
    assert not any(item.label == "Delete selected calculation" for item in app.button)


def test_history_requires_confirmation_and_deletes_last_record(history_app):
    app, repository = history_app
    TargetService(repository).calculate_and_save(75, 175, 25, "Male", "moderate", "Maintain")
    app.run(timeout=10)
    assert not app.exception
    assert button(app, "Delete selected calculation").disabled
    next(item for item in app.checkbox if "deleting this record" in item.label).check().run()
    button(app, "Delete selected calculation").click().run(timeout=10)
    assert not app.exception
    assert repository.list_records() == []
    assert any(item.label == "Save daily entry" for item in app.button)


def test_edit_refreshes_displayed_targets(history_app):
    app, repository = history_app
    TargetService(repository).calculate_and_save(75, 175, 25, "Male", "moderate", "Maintain")
    app.run(timeout=10)
    assert not app.exception
    record_id = repository.list_records()[0]["id"]
    app.number_input(key=f"w_{record_id}").set_value(80)
    button(app, "Save edited calculation").click().run(timeout=10)
    assert not app.exception
    record = repository.get_record(record_id)
    assert record["weight_kg"] == 80
    assert any(item.value == f'{record["calories"]:,} kcal' for item in app.metric)
