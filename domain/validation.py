"""Supported input ranges for this adult-oriented project, not medical cutoffs."""

from math import isfinite

from domain.units import height_to_cm, pounds_to_kg


def validate_weight(weight_kg):
    if weight_kg <= 0:
        raise ValueError("Weight must be greater than zero.")
    if not isfinite(weight_kg) or not pounds_to_kg(50) <= weight_kg <= pounds_to_kg(500):
        raise ValueError("This app supports weights from 50 to 500 lb. Check your entry.")


def validate_measurements(weight_kg, height_cm, age):
    validate_weight(weight_kg)
    if height_cm <= 0:
        raise ValueError("Height must be greater than zero.")
    if not isfinite(height_cm) or not height_to_cm(3, 0) <= height_cm <= height_to_cm(8, 0):
        raise ValueError("This app supports heights from 3 ft 0 in to 8 ft 0 in. Check your entry.")
    if age <= 0:
        raise ValueError("Age must be greater than zero.")
    if not isfinite(age) or not 18 <= age <= 100 or age != int(age):
        raise ValueError("This app supports adults ages 18 to 100. Enter a whole-number age.")
