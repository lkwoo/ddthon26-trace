"""Weather formatting (distractor: unrelated to the questions)."""


def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert a temperature from Celsius to Fahrenheit."""
    return celsius * 9.0 / 5.0 + 32.0


def describe_sky(cloud_cover: float) -> str:
    """Describe the sky given a cloud-cover fraction between 0 and 1."""
    if cloud_cover < 0.2:
        return "clear"
    if cloud_cover < 0.7:
        return "partly cloudy"
    return "overcast"
