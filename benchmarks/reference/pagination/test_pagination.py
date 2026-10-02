import unittest
from unittest.mock import Mock
from solution import collect


class PaginationTests(unittest.TestCase):
    def test_empty_middle_page_and_deduplication(self):
        fetch = Mock(side_effect=[
            {"items": [{"id": "a", "value": 1}], "next": "p2"},
            {"items": [], "next": "p3"},
            {"items": [{"id": "a", "value": 2}, {"id": "b"}], "next": None},
        ])
        result = collect(fetch)
        self.assertEqual(result, [{"id": "a", "value": 1}, {"id": "b"}])
        self.assertEqual([call.args for call in fetch.call_args_list], [(None,), ("p2",), ("p3",)])

    def test_midstream_failure(self):
        fetch = Mock(side_effect=[{"items": [{"id": "a"}], "next": "p2"}, OSError("HTTP 500")])
        with self.assertRaises(OSError):
            collect(fetch)

    def test_repeated_cursor(self):
        fetch = Mock(return_value={"items": [], "next": "p2"})
        with self.assertRaisesRegex(ValueError, "cursor"):
            collect(fetch)
        self.assertEqual(fetch.call_count, 2)

    def test_schema_and_empty_result(self):
        self.assertEqual(collect(lambda _: {"items": [], "next": None}), [])
        for page in [None, {}, {"items": [None], "next": None}, {"items": [], "next": 2}]:
            with self.subTest(page=page), self.assertRaises(ValueError):
                collect(lambda _: page)
