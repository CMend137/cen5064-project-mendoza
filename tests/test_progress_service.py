from datetime import date

import pytest

from data.target_repository import TargetRepository
from domain.progress import progress_recommendation, weekly_summary
from services.progress_service import ProgressService


def test_weekly_summary_and_recommendation():
    logs = [{"log_date": "2026-11-04", "weight_kg": 75.0, "calories": 2100},
            {"log_date": "2026-11-07", "weight_kg": 74.5, "calories": 2000}]
    summary = weekly_summary(logs)
    assert summary["average_calories"] == 2050
    assert summary["weight_change_kg"] == -0.5
    assert "trending downward" in progress_recommendation("lose", summary)


def test_log_validation_and_week_filter(tmp_path):
    service = ProgressService(TargetRepository(tmp_path / "nutrition.db"))
    with pytest.raises(ValueError):
        service.save_daily_log("2026-11-07", 0, 2000)
    with pytest.raises(ValueError):
        service.save_daily_log("2026-11-07", 75, -1)
    service.save_daily_log("2026-10-01", 75, 2100)
    service.save_daily_log("2026-11-07", 74, 2000)
    assert service.weekly_summary(date(2026, 11, 7))["days_logged"] == 1
    assert len(service.list_daily_logs()) == 2
