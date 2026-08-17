# Known Failure Modes

## 1. Process restart while a delivery is in memory
If the application process stops after a delivery is added to the database but before the background worker processes it, the in-memory queue is lost. The delivery remains persisted in the database, but this implementation does not automatically rebuild the queue after restart.

## 2. PseudoGram remains unavailable
If the mock DM API is unavailable or repeatedly returns temporary errors, the worker retries the delivery up to 5 attempts. After the retry limit is reached, the delivery is marked as `failed`.

## 3. Rate limiting
If the mock API returns HTTP 429, the worker waits using the `Retry-After` value and places the delivery back into the queue. If repeated failures consume the retry limit, the delivery can eventually be marked as failed.

## 4. Duplicate protection scope
A duplicate DM is blocked for the same `rule_id` and `user_id`. This means a user will not receive another DM for the same rule, even if they make another matching comment.

## 5. Statistics during concurrent processing
The `/stats` endpoint reads the current database state. Statistics can change while background workers are processing deliveries, so a request made during processing may observe an intermediate state.

## 6. In-memory worker queue
The background queue is process-local. Running multiple application processes would create separate queues, so a production deployment would require a shared durable queue such as Redis or a task broker.

## 7. External API response differences
The mock API may return a successful response with HTTP 200 and a queued DM response. The worker accepts both HTTP 200 and HTTP 202 as successful submission responses.