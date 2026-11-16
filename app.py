"""MacroMetric's multi-tab Streamlit presentation layer."""

from datetime import date

import pandas as pd
import streamlit as st

from data.target_repository import TargetRepository
from domain.units import cm_to_height, height_to_cm, kg_to_pounds, pounds_to_kg
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


st.markdown("""<style>
.stApp {background: #0b1120; color: #e6edf7;}
.block-container {max-width: 1240px; padding-top: 2rem;}
[data-testid="stHeader"] {background: #0b1120;}
[data-testid="stMetric"] {background: #172338; border: 1px solid #33445e;
 border-top: 3px solid #60a5fa; border-radius: 14px; padding: 18px;}
[data-testid="stMetricLabel"] {color: #bac9dd;}
[data-testid="stMetricValue"] {color: #f4f7fc;}
[data-testid="stForm"] {background: #111c2e; border: 1px solid #33445e;
 border-radius: 18px; padding: 24px;}
[data-baseweb="tab-list"] {gap: 8px; padding: 8px; background: #111c2e;
 border-radius: 12px; overflow-x: auto;}
[data-baseweb="tab"] {padding: 10px 16px; border-radius: 8px; color: #c5d3e6;}
[data-baseweb="tab"][aria-selected="true"] {background: #233c62; color: #ffffff;}
h1, h2, h3 {letter-spacing: -0.025em;}
.mm-hero {background: linear-gradient(115deg, #172b4d, #1c2341);
 border: 1px solid #3c5278; border-radius: 22px; padding: 30px; margin-bottom: 24px;}
.mm-hero h1 {color: #ffffff; margin: 8px 0; font-size: clamp(2rem, 5vw, 3rem);}
.mm-hero p {color: #c5d3e6; margin: 0;}
.mm-eyebrow {color: #93c5fd; font-size: .8rem; font-weight: 700; letter-spacing: .16em;}
@media (max-width: 640px) {
 .block-container {padding: 1rem;} .mm-hero {padding: 20px;}
 [data-testid="stForm"] {padding: 16px;}
}
</style>""", unsafe_allow_html=True)
st.markdown("""<section class="mm-hero">
<div class="mm-eyebrow">PLAN • TRACK • UNDERSTAND</div>
<h1>MacroMetric</h1>
<p>Your nutrition targets. Your daily progress. One clear view.</p>
</section>""", unsafe_allow_html=True)
if "notice" in st.session_state:
    st.success(st.session_state.pop("notice"))
saved_records = target_service.list_calculations()
latest = saved_records[0] if saved_records else {}
st.caption(f"Saved goal: {str(latest.get('goal') or 'Not set').title()} · Measurements in lb and ft/in")
with st.container(border=True):
    st.subheader("Your day at a glance")
    today_log = next((row for row in progress_service.list_daily_logs()
                      if row["log_date"] == date.today().isoformat()), None)
    daily_target = latest.get("calories")
    consumed = today_log["calories"] if today_log else None
    a, b, c = st.columns(3)
    a.metric("Daily target", f"{daily_target:,} kcal" if daily_target else "Not set")
    b.metric("Logged today", f"{consumed:,} kcal" if consumed is not None else "No entry")
    if consumed is not None and daily_target:
        remaining = daily_target - consumed
        c.metric("Above target" if remaining < 0 else "Remaining", f"{abs(remaining):,} kcal")
        ratio = consumed / daily_target
        st.progress(min(max(ratio, 0.0), 1.0), text=f"{ratio:.0%} of daily calorie target logged")
    else:
        c.metric("Days logged this week", f"{len(progress_service.weekly_logs())} / 7")
        st.caption("Save a target in Calculator and an entry for today in Daily Log to see your calorie progress.")

calculator, history, daily_log, trends, recommendations = st.tabs(
    ["Calculator", "Calculation History", "Daily Log", "Weekly Trends", "Recommendations"]
)

with calculator:
    st.subheader("Calculate daily nutrition targets")
    st.caption("Supported inputs: 50–500 lb · 3 ft 0 in–8 ft 0 in · ages 18–100. Values outside these ranges cannot be saved.")
    with st.form("new_calculation"):
        a, b, c = st.columns(3)
        with a:
            weight_lb = st.number_input("Weight (lb)", min_value=1.0, value=165.0, step=0.1)
            sex = st.selectbox("Sex", SEX_OPTIONS)
        with b:
            height_ft = st.number_input("Height — feet", min_value=0, max_value=9, value=5)
            height_in = st.number_input("Height — inches", min_value=0.0, max_value=11.99, value=9.0, step=0.1)
            activity = st.selectbox("Activity level", ACTIVITY_OPTIONS, index=2)
        with c:
            age = st.number_input("Age", min_value=1, value=25, step=1)
            goal = st.selectbox("Fitness goal", GOAL_OPTIONS,
                                index=GOAL_OPTIONS.index(str(latest.get("goal") or "Lose").title()))
        submitted = st.form_submit_button("Calculate and save", type="primary")
    if submitted:
        try:
            result = target_service.calculate_and_save(
                pounds_to_kg(weight_lb), height_to_cm(height_ft, height_in), age, sex, activity_value(activity), goal
            )
            st.session_state["notice"] = "Your goal and daily targets are saved!"
            st.rerun()
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
        table_columns = ["id", "created_at", "goal", "Weight (lb)", "calories",
                         "protein", "carbohydrates", "fat"]
        record_frame = pd.DataFrame(records)
        record_frame["Weight (lb)"] = record_frame["weight_kg"].apply(lambda v: round(kg_to_pounds(v), 1) if pd.notna(v) else None)
        st.dataframe(record_frame[table_columns], hide_index=True, use_container_width=True)
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
            st.caption("Supported inputs: 50–500 lb · 3 ft 0 in–8 ft 0 in · ages 18–100.")
            with st.form(f"edit_calculation_{chosen_id}"):
                x, y, z = st.columns(3)
                with x:
                    edit_weight = st.number_input(
                        "Weight (lb)", min_value=1.0,
                        value=kg_to_pounds(selected["weight_kg"]), step=0.1, key=f"w_{chosen_id}"
                    )
                    edit_sex = st.selectbox(
                        "Sex", SEX_OPTIONS, index=SEX_OPTIONS.index(selected["sex"].capitalize()),
                        key=f"s_{chosen_id}",
                    )
                with y:
                    feet, inches = cm_to_height(selected["height_cm"])
                    edit_feet = st.number_input("Height — feet", min_value=0, value=feet, key=f"hf_{chosen_id}")
                    edit_inches = st.number_input("Height — inches", min_value=0.0, max_value=11.99,
                                                  value=inches, step=0.1, key=f"hi_{chosen_id}")
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
                        chosen_id, weight_kg=pounds_to_kg(edit_weight), height_cm=height_to_cm(edit_feet, edit_inches),
                        age=edit_age, sex=edit_sex,
                        activity_level=activity_value(edit_activity), goal=edit_goal,
                    )
                    st.session_state["notice"] = "Calculation updated."
                    st.rerun()
                except ValueError as error:
                    st.error(str(error))
        confirm = st.checkbox("I understand deleting this record cannot be undone.",
                              key=f"confirm_delete_{chosen_id}")
        if st.button("Delete selected calculation", disabled=not confirm):
            target_service.delete_calculation(chosen_id)
            st.session_state["notice"] = "Calculation deleted."
            st.rerun()

with daily_log:
    st.subheader("Daily intake and weight")
    st.write("Choose a date and save intake/weight. Re-saving an existing date edits that entry.")
    st.caption("Supported weight: 50–500 lb. Check your units before saving.")
    with st.form("daily_progress"):
        log_date = st.date_input("Date", value=date.today())
        x, y = st.columns(2)
        with x:
            logged_weight = st.number_input("Weight (lb)", min_value=0.1, value=165.0, step=0.1)
        with y:
            calories_eaten = st.number_input("Calories consumed", min_value=0, value=2000, step=50)
        save_log = st.form_submit_button("Save daily entry", type="primary")
    if save_log:
        try:
            progress_service.save_daily_log(log_date, pounds_to_kg(logged_weight), calories_eaten)
            st.session_state["notice"] = f"Daily entry for {log_date} saved."
            st.rerun()
        except ValueError as error:
            st.error(str(error))
    logs = progress_service.list_daily_logs()
    if logs:
        log_frame = pd.DataFrame(logs)
        log_frame["Weight (lb)"] = log_frame.pop("weight_kg").apply(lambda v: round(kg_to_pounds(v), 1))
        st.dataframe(log_frame.rename(columns={"log_date": "Date", "calories": "Calories"}), use_container_width=True, hide_index=True)
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
        trend_frame["Weight (lb)"] = trend_frame["weight_kg"].apply(kg_to_pounds)
        st.markdown("#### Weight (lb)")
        st.line_chart(trend_frame[["Weight (lb)"]], color="#60a5fa")
        st.markdown("#### Daily calories consumed")
        st.bar_chart(trend_frame[["calories"]], color="#a78bfa")
        x, y, z = st.columns(3)
        x.metric("Days logged", summary["days_logged"])
        y.metric("Average weight", f'{kg_to_pounds(summary["average_weight_kg"]):.1f} lb')
        z.metric("Average calories", f'{summary["average_calories"]:,} kcal')
        st.caption(f'Weight change from first to last logged day: {kg_to_pounds(summary["weight_change_kg"]):+.2f} lb')

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
