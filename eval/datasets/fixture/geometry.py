"""Geometry helpers (distractor: unrelated to the questions)."""

import math


def circle_area(radius: float) -> float:
    """Return the area of a circle with the given radius."""
    return math.pi * radius * radius


def rectangle_perimeter(width: float, height: float) -> float:
    """Return the perimeter of a rectangle."""
    return 2.0 * (width + height)
