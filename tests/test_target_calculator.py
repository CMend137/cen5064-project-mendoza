import pytest

from domain.target_calculator import calculate_targets

def test_calculate_targets_maintain():
    result = calculate_targets(
        weight_kg=75,
        height_cm=175,
        age=30,
        sex="male",
        activity_level="moderate",
        goal="maintain",
    )

    assert result["calories"] == 2633
    assert result["protein"] == 150
    assert result["fat"] == 73
    assert result["carbohydrates"] == 344


def test_invalid_goal_raises_error():
    with pytest.raises(ValueError):
        calculate_targets(
            weight_kg=75,
            height_cm=175,
            age=30,
            sex="male",
            activity_level="moderate",
            goal="cut",
        )


def test_invalid_weight_raises_error():
    with pytest.raises(ValueError):
        calculate_targets(
            weight_kg=0,
            height_cm=175,
            age=30,
            sex="male",
            activity_level="moderate",
            goal="maintain",
        )
