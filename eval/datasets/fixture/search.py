"""Document search for the fixture app."""


def search_documents(query: str, documents: list[str]) -> list[str]:
    """Search documents for a query string, returning matches ranked by relevance."""
    q = query.lower()
    scored = [(doc.lower().count(q), doc) for doc in documents]
    scored = [(score, doc) for score, doc in scored if score > 0]
    scored.sort(key=lambda sd: (-sd[0], sd[1]))
    return [doc for _, doc in scored]
