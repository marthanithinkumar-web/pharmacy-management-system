# Test cases — Pharmacy Management System

Run the automated tests with `python -m unittest discover -s tests -v`. The expected outcomes below describe the test oracle; fill the **Actual result** column from the real run before submitting the college report.

| ID | Scenario | Input / action | Expected result | Actual result |
|---|---|---|---|---|
| TC-01 | Dashboard | Open `/` | HTTP 200; metrics and reports render | Record after run |
| TC-02 | Add medicine | Submit a valid name and reorder level | Medicine appears in catalogue | Record after run |
| TC-03 | Missing medicine name | Submit empty name | Validation message; no invalid row | Manual check |
| TC-04 | Receive stock | Valid medicine, future expiry, positive quantity | Batch, purchase, purchase item and movement are recorded | Manual check |
| TC-05 | Duplicate batch | Reuse a batch number for the same medicine | Friendly validation message; transaction rolled back | Manual check |
| TC-06 | Complete sale | Select valid unexpired batch and quantity within stock | Invoice created; stock decreases by quantity sold | Automated test |
| TC-07 | Insufficient stock | Request more units than available | Sale rejected; no invoice and no stock change | Automated test |
| TC-08 | Expired batch | Attempt to sell a batch whose expiry is before today | Batch not offered / sale rejected | Manual check |
| TC-09 | Low-stock report | Stock is at or below reorder level | Medicine appears in low-stock report | Manual check |
| TC-10 | Expiry report | Batch expires within 90 days and has stock | Batch appears in expiry report | Manual check |
| TC-11 | Foreign-key integrity | Insert line item referencing nonexistent batch | Database rejects the operation | SQL check |
| TC-12 | Daily sales aggregation | Record two sales on the same day | Daily report groups bills and sums revenue | Manual check |

## Expected transactional behaviour
The sale workflow should be atomic. If any selected line is invalid, the transaction must roll back: no partial sale header, sale items, stock decrements or stock-movement entries remain.

## Evidence for report
Capture genuine screenshots after running the application: dashboard, medicine catalogue, receiving stock form, completed invoice, low-stock/expiry report, and terminal test output. Do not paste mock screenshots or claim a test passed without running it.
