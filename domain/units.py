"""Presentation conversions; calculations and stored values remain metric."""


def pounds_to_kg(pounds):
    return pounds * 0.45359237


def kg_to_pounds(kg):
    return kg / 0.45359237


def height_to_cm(feet, inches):
    return (feet * 12 + inches) * 2.54


def cm_to_height(cm):
    total = cm / 2.54
    feet = int(total // 12)
    return feet, total - feet * 12
