# Pricing contract

Implement tests for `solution.total_cents(subtotal)` using Python unittest.

- Subtotal is integer cents, at least zero. Reject booleans, floats, strings,
  null and negative values with ValueError.
- At an original subtotal of 10,000 cents or more, apply a 10% discount.
  Round the discounted amount to the nearest cent, with halves rounded up.
- Shipping is 499 cents below an original subtotal of 5,000 cents, otherwise zero.
- Return discounted subtotal plus shipping as an integer. No external I/O or state.
- Concurrency and external failure modes are not applicable to this pure function.
