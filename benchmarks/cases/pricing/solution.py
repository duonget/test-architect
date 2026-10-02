"""Integer money calculation with explicit half-up rounding."""


def total_cents(subtotal):
    if type(subtotal) is not int or subtotal < 0:
        raise ValueError("subtotal must be a non-negative integer")
    # Ten percent discount starts at 10,000 cents; round half up.
    discounted = (subtotal * 90 + 50) // 100 if subtotal >= 10_000 else subtotal
    shipping = 0 if subtotal >= 5_000 else 499
    return discounted + shipping
