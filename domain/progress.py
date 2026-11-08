"""Pure functions for weekly progress summaries and transparent recommendations."""

from statistics import mean


def weekly_summary(logs):
    if not logs:
        return None
    ordered = sorted(logs, key=lambda x: x["log_date"])
    return {
        "days_logged": len(ordered),
        "average_weight_kg": round(mean(log["weight_kg"] for log in ordered), 2),
        "average_calories": round(mean(log["calories"] for log in ordered)),
        "weight_change_kg": round(
            ordered[-1]["weight_kg"] - ordered[0]["weight_kg"], 2
        ),
    }


def progress_recommendation(goal, summary):
    """Simple rules for a one-week trend; not medical or dietary advice."""
    if summary is None or summary["days_logged"] < 2:
        return "Log at least two days to see a preliminary progress recommendation."

    change = summary["weight_change_kg"]
    goal = goal.lower()
    if goal == "lose":
        if change < -1:
            return "Weight is falling quickly. Consider reviewing your intake and checking with a qualified professional."
        if change > -0.1:
            return "Weight is relatively stable this week. Continue logging and review your consistency."
        return "Weight is trending downward. Continue monitoring your weekly average."
    if goal == "gain":
        if change > 1:
            return "Weight is rising quickly. Review intake and monitor your trend."
        if change < 0.1:
            return "Weight is relatively stable. Continue tracking and review your intake."
        return "Weight is trending upward. Continue monitoring your weekly average."
    if goal == "maintain":
        if abs(change) > 0.5:
            return "Weight has shifted this week. Keep tracking to determine whether this is a sustained change."
        return "Weight is relatively stable this week."
    return "Choose a valid goal to receive a rule-based recommendation."
