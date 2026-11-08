"""MacroMetric's multi-tab Streamlit presentation layer."""

from datetime import date

import pandas as pd
import streamlit as st

from data.target_repository import TargetRepository
from services.progress_service import ProgressService
from services.target_service import TargetService


st.set_page_config(page_title="MacroMetric", page_icon="📊", layout="wide")

repository = TargetRepository()
target_service = TargetService(repository)
progress_service = ProgressService(repository)

ACTIVITY_OPTIONS = ["Sedentary", "Light", "Moderate", "Active", "Very Active"]
GOAL_OPTIONS = ["Lose", "Maintain", "Gain"]
SEX_OPTIONS = ["Male", "Female"]


def activity_value(text):
    return text.lower().replace(" ", "_")


def show_targets(targets):
    columns = st.columns(4)
    columns[0].metric("Calories", f'{targets["calories"]:,} kcal')
    columns[1].metric("Protein", f'{targets["protein"]} g')
    columns[2].metric("Carbohydrates", f'{targets["carbohydrates"]} g')
    columns[3].metric("Fat", f'{targets["fat"]} g')


st.title("📊 MacroMetric")
st.caption("Nutrition target planning, calculation history, and daily progress in one place.")
calculator, history, daily_log, trends, recommendations = st.tabs(
    ["Calculator", "Calculation History", "Daily Log", "Weekly Trends", "Recommendations"]
)

with calculator:
    st.subheader("Calculate daily nutrition targets")
    with st.form("new_calculation"):
        a, b, c = st.columns(3)
        with a:
            weight_kg = st.number_input("Weight (kg)", min_value=1.0, value=75.0, step=0.1)
            sex = st.selectbox("Sex", SEX_OPTIONS)
        with b:
            height_cm = st.number_input("Height (cm)", min_value=1.0, value=175.0, step=0.1)
            activity = st.selectbox("Activity level", ACTIVITY_OPTIONS, index=2)
        with c:
            age = st.number_input("Age", min_value=1, value=25, step=1)
            goal = st.selectbox("Fitness goal", GOAL_OPTIONS)
        submitted = st.form_submit_button("Calculate and save", type="primary")
    if submitted:
        try:
            result = target_service.calculate_and_save(
                weight_kg, height_cm, age, sex, activity_value(activity), goal
            )
            st.success("Calculated and saved to the SQLite database.")
            show_targets(result)
        except ValueError as error:
            st.error(str(error))
    latest_targets = target_service.get_saved_targets()
    if latest_targets:
        st.divider()
        st.subheader("Latest saved targets")
        show_targets(latest_targets)

with history:
    st.subheader("Calculation history")
    records = target_service.list_calculations()
    if not records:
        st.info("No saved calculations. Create one in the Calculator tab.")
    else:
        table_columns = ["id", "created_at", "goal", "weight_kg", "calories",
                         "protein", "carbohydrates", "fat"]
        st.dataframe(pd.DataFrame(records)[table_columns], hide_index=True, use_container_width=True)
        chosen_id = st.selectbox(
            "Select a calculation to view, edit, or delete",
            options=[record["id"] for record in records],
            format_func=lambda record_id: f"Record #{record_id}",
        )
        selected = target_service.get_calculation(chosen_id)
        st.write(f'**Record #{chosen_id}** — saved {selected["created_at"]} (UTC)')
        show_targets(selected)

        required = ["weight_kg", "height_cm", "age", "sex", "activity_level", "goal"]
        if any(selected[field] is None for field in required):
            st.warning("This legacy record has no saved input values, so it cannot be recalculated.")
        else:
            st.markdown("#### Edit and recalculate")
            with st.form(f"edit_calculation_{chosen_id}"):
                x, y, z = st.columns(3)
                with x:
                    edit_weight = st.number_input(
                        "Weight (kg)", min_value=1.0,
                        value=float(selected["weight_kg"]), step=0.1, key=f"w_{chosen_id}"
                    )
                    edit_sex = st.selectbox(
                        "Sex", SEX_OPTIONS, index=SEX_OPTIONS.index(selected["sex"].capitalize()),
                        key=f"s_{chosen_id}",
                    )
                with y:
                    edit_height = st.number_input(
                        "Height (cm)", min_value=1.0,
                        value=float(selected["height_cm"]), step=0.1, key=f"h_{chosen_id}"
                    )
                    activity_label = selected["activity_level"].replace("_", " ").title()
                    edit_activity = st.selectbox(
                        "Activity level", ACTIVITY_OPTIONS,
                        index=ACTIVITY_OPTIONS.index(activity_label), key=f"a_{chosen_id}"
                    )
                with z:
                    edit_age = st.number_input(
                        "Age", min_value=1, value=int(selected["age"]),
                        key=f"age_{chosen_id}",
                    )
                    edit_goal = st.selectbox(
                        "Fitness goal", GOAL_OPTIONS,
                        index=GOAL_OPTIONS.index(selected["goal"].capitalize()),
                        key=f"g_{chosen_id}",
                    )
                update = st.form_submit_button("Save edited calculation")
            if update:
                try:
                    target_service.edit_calculation(
                        chosen_id, weight_kg=edit_weight, height_cm=edit_height,
                        age=edit_age, sex=edit_sex,
                        activity_level=activity_value(edit_activity), goal=edit_goal,
                    )
                    st.success("Record updated. Open this tab again to refresh values.")
                except ValueError as error:
                    st.error(str(error))
        confirm = st.checkbox("I understand deleting this record cannot be undone.",
                              key=f"confirm_delete_{chosen_id}")
        if st.button("Delete selected calculation", disabled=not confirm):
            if target_service.delete_calculation(chosen_id):
                st.success("Record deleted.")
                st.rerun()

with daily_log:
    st.subheader("Daily intake and weight")
    st.write("Choose a date and save intake/weight. Re-saving an existing date edits that entry.")
    with st.form("daily_progress"):
        log_date = st.date_input("Date", value=date.today())
        x, y = st.columns(2)
        with x:
            logged_weight = st.number_input("Weight (kg)", min_value=0.1, value=75.0, step=0.1)
        with y:
            calories_eaten = st.number_input("Calories consumed", min_value=0, value=2000, step=50)
        save_log = st.form_submit_button("Save daily entry", type="primary")
    if save_log:
        try:
            progress_service.save_daily_log(log_date, logged_weight, calories_eaten)
            st.success(f"Daily entry for {log_date} saved.")
        except ValueError as error:
            st.error(str(error))
    logs = progress_service.list_daily_logs()
    if logs:
        st.dataframe(pd.DataFrame(logs), use_container_width=True, hide_index=True)
        delete_date = st.selectbox(
            "Select an entry date to delete", options=[log["log_date"] for log in logs]
        )
        confirm_day = st.checkbox("Confirm deletion of selected daily entry")
        if st.button("Delete daily entry", disabled=not confirm_day):
            progress_service.delete_daily_log(delete_date)
            st.success(f"Entry for {delete_date} deleted.")
            st.rerun()
    else:
        st.info("No daily entries saved yet.")

with trends:
    st.subheader("Last 7 days of progress")
    week_logs = progress_service.weekly_logs()
    summary = progress_service.weekly_summary()
    if not week_logs:
        st.info("Log some days in Daily Log to see your charts.")
    else:
        trend_frame = pd.DataFrame(week_logs)
        trend_frame["log_date"] = pd.to_datetime(trend_frame["log_date"])
        trend_frame = trend_frame.set_index("log_date")
        st.markdown("#### Weight (kg)")
        st.line_chart(trend_frame[["weight_kg"]])
        st.markdown("#### Daily calories consumed")
        st.bar_chart(trend_frame[["calories"]])
        x, y, z = st.columns(3)
        x.metric("Days logged", summary["days_logged"])
        y.metric("Average weight", f'{summary["average_weight_kg"]} kg')
        z.metric("Average calories", f'{summary["average_calories"]:,} kcal')
        st.caption(f'Weight change from first to last logged day: {summary["weight_change_kg"]:+.2f} kg')

with recommendations:
    st.subheader("Rule-based progress recommendations")
    saved = target_service.list_calculations()
    if not saved:
        st.info("Save a calculator goal first to receive progress recommendations.")
    else:
        selected_goal = next((row["goal"] for row in saved if row["goal"]), None)
        if not selected_goal:
            st.info("No saved fitness goal is available yet.")
        else:
            st.write(f"**Most recently calculated goal:** {selected_goal.title()}")
            st.info(progress_service.recommendation(selected_goal))
            st.caption("Recommendations use simple, transparent rules and are not individualized medical advice. More logged days improve trend interpretation.")
