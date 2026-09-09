"""Notifications delivery for the fixture app."""


def send_notification(user_id: str, message: str, channel: str = "email") -> bool:
    """Send a notification message to a user over the given delivery channel."""
    if channel not in _CHANNELS:
        return False
    return _CHANNELS[channel](user_id, message)


def _send_email(user_id: str, message: str) -> bool:
    return True


def _send_sms(user_id: str, message: str) -> bool:
    return True


_CHANNELS = {"email": _send_email, "sms": _send_sms}
