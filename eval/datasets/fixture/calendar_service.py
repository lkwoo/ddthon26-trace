"""Calendar scheduling (distractor: unrelated to the questions)."""


def is_leap_year(year: int) -> bool:
    """Return True if the given year is a leap year."""
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def days_in_month(year: int, month: int) -> int:
    """Return the number of days in a given month of a given year."""
    lengths = [31, 29 if is_leap_year(year) else 28, 31, 30, 31, 30,
               31, 31, 30, 31, 30, 31]
    return lengths[month - 1]
