def calculate_targets(
    weight_kg,
    height_cm,
    age,
    sex,
    activity_level,
    goal
):
    """Calculate daily calorie and macronutrient targets.

    Weight must be provided in kilograms and height in centimeters.
    """

    if weight_kg <= 0:
        raise ValueError("Weight must be greater than zero.")

    if height_cm <= 0:
        raise ValueError("Height must be greater than zero.")

    if age <= 0:
        raise ValueError("Age must be greater than zero.")

    sex = sex.lower()
    activity_level = activity_level.lower()
    goal = goal.lower()

    activity_multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9,
    }

    goal_adjustments = {
        "lose": -500,
        "maintain": 0,
        "gain": 500,
    }

    if activity_level not in activity_multipliers:
        raise ValueError("Invalid activity level.")

    if goal not in goal_adjustments:
        raise ValueError("Invalid fitness goal.")

    if sex == "male":
        sex_adjustment = 5
    elif sex == "female":
        sex_adjustment = -161
    else:
        raise ValueError("Sex must be 'male' or 'female'.")

    # Mifflin-St Jeor equation
    bmr = (
        (10 * weight_kg)
        + (6.25 * height_cm)
        - (5 * age)
        + sex_adjustment
    )

    maintenance_calories = (
        bmr * activity_multipliers[activity_level]
    )

    target_calories = (
        maintenance_calories
        + goal_adjustments[goal]
    )

    if target_calories <= 0:
        raise ValueError("Calculated calorie target must be positive.")

    protein_grams = weight_kg * 2.0
    fat_grams = (target_calories * 0.25) / 9

    carbohydrate_calories = (
        target_calories
        - (protein_grams * 4)
        - (fat_grams * 9)
    )

    if carbohydrate_calories < 0:
        raise ValueError(
            "Calculated carbohydrate target cannot be negative."
        )

    carbohydrate_grams = carbohydrate_calories / 4

    return {
        "calories": round(target_calories),
        "protein": round(protein_grams),
        "fat": round(fat_grams),
        "carbohydrates": round(carbohydrate_grams),
    }
