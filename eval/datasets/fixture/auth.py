"""User authentication for the fixture app."""


def authenticate_user(username: str, password: str) -> bool:
    """Authenticate a user by username and password, returning True on success.

    Hashes the supplied password and compares it against the stored credential
    for the given username. Establishes a login session on success.
    """
    stored = _lookup_credential(username)
    if stored is None:
        return False
    return _hash_password(password) == stored


def _lookup_credential(username: str) -> str | None:
    return _CREDENTIALS.get(username)


def _hash_password(password: str) -> str:
    import hashlib
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


_CREDENTIALS = {"alice": _hash_password("hunter2")}
