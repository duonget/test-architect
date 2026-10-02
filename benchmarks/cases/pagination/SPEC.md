# Pagination contract

Test `solution.collect(fetch)` using Python unittest. `fetch(cursor)` is an external
HTTP boundary, represented by a synchronous callable; its first cursor is None.

- Each page is a dict with `items` (list) and `next` (None or nonempty string).
- Each item is a dict with a string `id`. Preserve the first occurrence of each ID
  and encounter order, including duplicates across pages.
- An empty items list does not stop traversal when a next cursor exists.
- Only next=None ends traversal. A repeated next cursor raises ValueError before
  fetching it again. Invalid page, item or cursor schemas also raise ValueError.
- Fetch exceptions propagate, including errors after earlier successful pages;
  never return partial success or silently retry.
- Calls have independent state. Async concurrency is not applicable.
