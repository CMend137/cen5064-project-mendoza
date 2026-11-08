"""SQLite persistence for MacroMetric calculations and daily progress logs."""

import sqlite3
from pathlib import Path


class TargetRepository:
    """Store calculation history and daily progress in a local SQLite database.

    All SQL parameters are bound; database connections are short lived so
    Streamlit's repeated page reruns do not retain stale database handles.
    """

    def __init__(self, file_path="data/macrometric.db"):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self):
        connection = sqlite3.connect(self.file_path, timeout=10)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self):
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS calculations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    weight_kg REAL,
                    height_cm REAL,
                    age INTEGER,
                    sex TEXT,
                    activity_level TEXT,
                    goal TEXT,
                    calories INTEGER NOT NULL,
                    protein INTEGER NOT NULL,
                    fat INTEGER NOT NULL,
                    carbohydrates INTEGER NOT NULL
                );
                CREATE TABLE IF NOT EXISTS daily_logs (
                    log_date TEXT PRIMARY KEY,
                    weight_kg REAL NOT NULL CHECK(weight_kg > 0),
                    calories INTEGER NOT NULL CHECK(calories >= 0),
                    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
                );
                """
            )

    def save(self, targets, inputs=None):
        """Append a calculation. Return its database ID.

        ``inputs`` is optional for older callers that only saved targets.
        All new app calculations supply their input values.
        """
        inputs = inputs or {}
        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO calculations (
                    weight_kg, height_cm, age, sex, activity_level, goal,
                    calories, protein, fat, carbohydrates
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    inputs.get("weight_kg"), inputs.get("height_cm"),
                    inputs.get("age"), inputs.get("sex"),
                    inputs.get("activity_level"), inputs.get("goal"),
                    targets["calories"], targets["protein"],
                    targets["fat"], targets["carbohydrates"],
                ),
            )
            return cursor.lastrowid

    def load(self):
        """Return the most recent target results, retaining the original API."""
        with self._connect() as conn:
            record = conn.execute(
                """SELECT calories, protein, fat, carbohydrates
                   FROM calculations ORDER BY id DESC LIMIT 1"""
            ).fetchone()
            return dict(record) if record else None

    def list_records(self):
        with self._connect() as conn:
            records = conn.execute(
                "SELECT * FROM calculations ORDER BY id DESC"
            ).fetchall()
            return [dict(record) for record in records]

    def get_record(self, record_id):
        with self._connect() as conn:
            record = conn.execute(
                "SELECT * FROM calculations WHERE id = ?", (record_id,)
            ).fetchone()
            return dict(record) if record else None

    def update_record(self, record_id, inputs, targets):
        """Recalculate and replace one record without changing its identity."""
        with self._connect() as conn:
            result = conn.execute(
                """
                UPDATE calculations SET
                    weight_kg=?, height_cm=?, age=?, sex=?, activity_level=?,
                    goal=?, calories=?, protein=?, fat=?, carbohydrates=?
                WHERE id=?
                """,
                (
                    inputs["weight_kg"], inputs["height_cm"],
                    inputs["age"], inputs["sex"], inputs["activity_level"],
                    inputs["goal"], targets["calories"],
                    targets["protein"], targets["fat"],
                    targets["carbohydrates"], record_id,
                ),
            )
            return result.rowcount > 0

    def delete_record(self, record_id):
        with self._connect() as conn:
            result = conn.execute(
                "DELETE FROM calculations WHERE id=?", (record_id,)
            )
            return result.rowcount > 0

    def save_log(self, log_date, weight_kg, calories):
        """Insert a new day or update the existing entry for that date."""
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO daily_logs (log_date, weight_kg, calories)
                VALUES (?, ?, ?)
                ON CONFLICT(log_date) DO UPDATE SET
                    weight_kg=excluded.weight_kg,
                    calories=excluded.calories,
                    updated_at=datetime('now')
                """,
                (log_date, weight_kg, calories),
            )

    def list_logs(self, start_date=None, end_date=None):
        sql = "SELECT log_date, weight_kg, calories FROM daily_logs WHERE 1=1"
        params = []
        if start_date is not None:
            sql += " AND log_date >= ?"
            params.append(start_date)
        if end_date is not None:
            sql += " AND log_date <= ?"
            params.append(end_date)
        sql += " ORDER BY log_date ASC"
        with self._connect() as conn:
            return [dict(row) for row in conn.execute(sql, params).fetchall()]

    def delete_log(self, log_date):
        with self._connect() as conn:
            result = conn.execute(
                "DELETE FROM daily_logs WHERE log_date=?", (log_date,)
            )
            return result.rowcount > 0
