"""Collect unique records while defending against repeated cursors."""


def collect(fetch):
    cursor = None
    seen_cursors = set()
    seen_ids = set()
    result = []
    while True:
        page = fetch(cursor)
        if not isinstance(page, dict) or not isinstance(page.get("items"), list) or "next" not in page:
            raise ValueError("page")
        for item in page["items"]:
            if not isinstance(item, dict) or not isinstance(item.get("id"), str):
                raise ValueError("item")
            if item["id"] not in seen_ids:
                seen_ids.add(item["id"])
                result.append(item)
        cursor = page["next"]
        if cursor is None:
            return result
        if not isinstance(cursor, str) or not cursor or cursor in seen_cursors:
            raise ValueError("cursor")
        seen_cursors.add(cursor)
