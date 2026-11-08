"""Application services for saved daily weight and calorie logs."""

from datetime import date, timedelta

from domain.progress import progress_recommendation, weekly_summary


class ProgressService:
    def __init__(self, repository):
        self.repository = repository

    def save_daily_log(self, log_date, weight_kg, calories):
        # Validate before any database writes.
        date.fromisoformat(str(log_date))
        if weight_kg <= 0:
            raise ValueError("Weight must be greater than zero.")
        if calories < 0:
            raise ValueError("Calorie intake cannot be negative.")
        self.repository.save_log(str(log_date), float(weight_kg), int(calories))

    def list_daily_logs(self):
        return self.repository.list_logs()

    def delete_daily_log(self, log_date):
        return self.repository.delete_log(str(log_date))

    def weekly_logs(self, ending_on=None):
        end = ending_on or date.today()
        start = end - timedelta(days=6)
        return self.repository.list_logs(start.isoformat(), end.isoformat())

    def weekly_summary(self, ending_on=None):
        return weekly_summary(self.weekly_logs(ending_on))

    def recommendation(self, goal, ending_on=None):
        return progress_recommendation(goal, self.weekly_summary(ending_on))
