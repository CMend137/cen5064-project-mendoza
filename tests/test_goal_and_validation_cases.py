"""Regression tests for goal calculations and invalid measurements."""

import pytest

from domain.target_calculator import calculate_targets

VALID_INPUTS = {
    "weight_kg": 75,
    "height_cm": 175,
    "age": 30,
    "sex": "male",
    "activity_level": "moderate",
}


def test_weight_loss_goal_calculates_reduced_targets():
    """A loss goal subtracts 500 calories from maintenance."""
    maintenance = calculate_targets(**VALID_INPUTS, goal="maintain")
    result = calculate_targets(**VALID_INPUTS, goal="lose")
    assert result == {"calories": 2133, "protein": 150, "fat": 59, "carbohydrates": 250}
    assert result["calories"] == maintenance["calories"] - 500


def test_weight_gain_goal_calculates_increased_targets():
    """A gain goal adds 500 calories to maintenance."""
    maintenance = calculate_targets(**VALID_INPUTS, goal="maintain")
    result = calculate_targets(**VALID_INPUTS, goal="gain")
    assert result == {"calories": 3133, "protein": 150, "fat": 87, "carbohydrates": 437}
    assert result["calories"] == maintenance["calories"] + 500


@pytest.mark.parametrize("height_cm", [0, -175])
def test_invalid_height_raises_error(height_cm):
    """Zero and negative heights must be rejected."""
    with pytest.raises(ValueError, match="Height must be greater than zero"):
        calculate_targets(**{**VALID_INPUTS, "height_cm": height_cm}, goal="maintain")


@pytest.mark.parametrize("age", [0, -30])
def test_invalid_age_raises_error(age):
    """Zero and negative ages must be rejected."""
    with pytest.raises(ValueError, match="Age must be greater than zero"):
        calculate_targets(**{**VALID_INPUTS, "age": age}, goal="maintain")
