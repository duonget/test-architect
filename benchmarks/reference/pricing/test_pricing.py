import unittest
from solution import total_cents


class PricingTests(unittest.TestCase):
    def test_boundaries_and_rounding(self):
        for subtotal, expected in [(0, 499), (4999, 5498), (5000, 5000),
                                   (9999, 9999), (10000, 9000), (10005, 9005)]:
            with self.subTest(subtotal=subtotal):
                self.assertEqual(total_cents(subtotal), expected)

    def test_invalid_inputs(self):
        for value in [None, True, "100", 1.5, -1]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                total_cents(value)
