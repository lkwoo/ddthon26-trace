"""User favorites and bookmarks for the fixture app."""


def count_favorites(user_id: str) -> int:
    """Count how many items a user has marked as favorites (bookmarks)."""
    return len(_FAVORITES.get(user_id, ()))


def add_favorite(user_id: str, item_id: str) -> None:
    """Mark an item as a favorite for the user."""
    _FAVORITES.setdefault(user_id, set()).add(item_id)


_FAVORITES: dict[str, set[str]] = {}
