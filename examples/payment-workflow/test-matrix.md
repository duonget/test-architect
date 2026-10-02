# 5-Dimensional Test Matrix: PaymentService

Formulated by **Test Architect** before writing tests.

| ID | Dimension | Scenario Description | Test Input / Setup | Expected Outcome |
| :--- | :--- | :--- | :--- | :--- |
| `TC-01` | **Happy Path** | Standard valid payment in USD | amount = 5000 ($50), USD, valid key | Return receipt, status `SUCCESS`, gateway called 1x |
| `TC-02` | **Happy Path** | Supported non-USD currencies | EUR, VND | Charges successfully |
| `TC-03` | **Boundary** | Minimum valid positive amount | amount = 1 cent | Passes validation |
| `TC-04` | **Boundary** | Zero amount | amount = 0 | Throws `InvalidAmount` |
| `TC-05` | **Boundary** | Negative amount | amount = -500 | Throws `InvalidAmount` |
| `TC-06` | **Boundary** | Maximum exact limit | amount = 1,000,000 cents ($10k) | Passes validation |
| `TC-07` | **Boundary** | Exceeds maximum limit by 1 cent | amount = 1,000,001 cents | Throws `AmountExceedsLimit` |
| `TC-08` | **Nullability** | Missing/empty idempotency key | key = `""` or whitespace | Throws `MissingIdempotencyKey` |
| `TC-09` | **Nullability** | Malformed request fields | unsupported currency, `NaN`/fractional amount, empty customer | Rejects before calling gateway |
| `TC-10` | **Failure Mode**| External gateway network failure | Gateway throws NetworkError | Exception propagates, key is NOT cached |
| `TC-11` | **Concurrency** | Duplicate calls overlap with same key and payload | 2 calls start before gateway resolves | Gateway charged only once; both calls share the result |
| `TC-12` | **Idempotency** | Same key is reused with a different payload | First amount = 1000, second amount = 2000 | Throws `IdempotencyKeyConflict`; no second charge |
