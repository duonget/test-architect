# Payment contract

Test `solution.Payments(gateway).pay(key, amount)` using Python unittest.

- `pay` is asynchronous. The external boundary is `await gateway.charge(key, amount)`.
- Key must be a nonblank string; amount must be a positive integer, excluding bool.
  Reject invalid fields with ValueError before external I/O.
- Overlapping calls with the same key and amount share one charge and its result.
  Completed successful calls also reuse that result.
- The same key with a different valid amount raises ValueError("conflict"), including
  while the original call is pending.
- Gateway failures propagate. A later call may retry a failed key.
- Cancelling one caller must not cancel the shared charge for other callers.
- Keys are forwarded unchanged to the gateway. Cross-process persistence and
  provider-side idempotency are outside this example's scope.
