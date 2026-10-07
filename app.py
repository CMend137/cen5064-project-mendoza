import streamlit as st

from services.target_service import TargetService


st.set_page_config(
    page_title="MacroMetric",
    page_icon="📊",
    layout="centered",
)

service = TargetService()

st.title("MacroMetric")
st.write(
    "Calculate personalized calorie and macronutrient targets "
    "based on your body measurements, activity level, and goal."
)

with st.form("target_form"):
    weight_kg = st.number_input(
        "Weight (kg)",
        min_value=1.0,
        value=75.0,
        step=0.1,
    )

    height_cm = st.number_input(
        "Height (cm)",
        min_value=1.0,
        value=175.0,
        step=0.1,
    )

    age = st.number_input(
        "Age",
        min_value=1,
        value=25,
        step=1,
    )

    sex = st.selectbox(
        "Sex",
        ["Male", "Female"],
    )

    activity_level = st.selectbox(
        "Activity Level",
        [
            "Sedentary",
            "Light",
            "Moderate",
            "Active",
            "Very Active",
        ],
    )

    goal = st.selectbox(
        "Fitness Goal",
        ["Lose", "Maintain", "Gain"],
    )

    submitted = st.form_submit_button("Calculate Targets")


if submitted:
    try:
        targets = service.calculate_and_save(
            weight_kg=weight_kg,
            height_cm=height_cm,
            age=age,
            sex=sex,
            activity_level=activity_level.lower().replace(" ", "_"),
            goal=goal,
        )

        st.success("Nutrition targets calculated and saved.")

        st.subheader("Your Daily Targets")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Calories", targets["calories"])
            st.metric("Protein", f'{targets["protein"]} g')

        with col2:
            st.metric("Carbohydrates", f'{targets["carbohydrates"]} g')
            st.metric("Fat", f'{targets["fat"]} g')

    except ValueError as error:
        st.error(str(error))


saved_targets = service.get_saved_targets()

if saved_targets:
    st.divider()
    st.subheader("Last Saved Targets")

    st.write(f'Calories: {saved_targets["calories"]}')
    st.write(f'Protein: {saved_targets["protein"]} g')
    st.write(f'Carbohydrates: {saved_targets["carbohydrates"]} g')
    st.write(f'Fat: {saved_targets["fat"]} g')