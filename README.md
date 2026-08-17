# LinkPlease Assignment

A FastAPI-based webhook processing system that detects keyword matches in comments and sends direct messages through the Pseudogram API.

## Overview

The application receives `comment.created` webhook events, checks the comment against configured keyword rules, creates a delivery record for matching users, and processes the DM asynchronously through a background worker.

The system also includes event deduplication, duplicate DM protection, retry handling, rate-limit handling, delivery status tracking, and a statistics endpoint.

## Features

- Keyword-based DM rules
- `comment.created` webhook processing
- Case-insensitive keyword matching
- Event deduplication using `event_id`
- Duplicate DM protection per rule and user
- Database-level uniqueness constraint
- Durable delivery records using SQLite
- Background DM worker
- Retry handling for temporary failures
- Rate-limit handling for HTTP `429` responses
- Maximum retry limit
- Delivery status tracking
- Statistics endpoint
- Docker deployment
- Pseudogram API integration

## Architecture

```text
                    Comment Event
                         |
                         v
                  POST /webhook
                         |
                         v
               Event Deduplication
                         |
                         v
                  Rule Matching
                         |
                         v
              Duplicate Protection
                         |
                         v
               Delivery DB Record
                         |
                         v
                Background Worker
                         |
                         v
                 Pseudogram API
                         |
                         v
              Delivery Status Update
                         |
                         v
                    /stats

PROJECT STRUCTURE:

linkplease-assignment/
│
├── app/
│   ├── database.py
│   ├── main.py
│   └── models.py
│
├── routes/
│   ├── rules.py
│   ├── stats.py
│   └── webhook.py
│
├── services/
│   ├── dm_service.py
│   ├── mock_api.py
│   ├── rule_service.py
│   ├── stats_service.py
│   └── webhook_service.py
│
├── workers/
│   └── dm_worker.py
│
├── Dockerfile
├── FAILURES.md
├── README.md
└── requirements.txt

Technology Stack
Python 3.11
FastAPI — REST API framework
SQLAlchemy — database ORM
SQLite — persistent local database
Pydantic — request validation
Uvicorn — ASGI server
Requests — external API communication
Docker — containerization
Render — deployment
Pseudogram API — mock social-media/DM API
API Endpoints
GET /

Returns the application status.

Example response:

{
  "message": "LinkPlease API is running"
}
POST /rules

Creates a keyword-based DM rule.

Example request:

{
  "keyword": "OFFER",
  "dm_message": "Here is the offer information!"
}

Example response:

{
  "rule_id": "generated-rule-id",
  "keyword": "OFFER",
  "dm_message": "Here is the offer information!"
}
POST /webhook

Receives a comment.created event.

Example request:

{
  "event_id": "evt_example_001",
  "event_type": "comment.created",
  "sent_at": "2026-08-17T12:12:00Z",
  "data": {
    "comment_id": "cmt_example_001",
    "post_id": "post_test_001",
    "text": "OFFER please",
    "created_at": "2026-08-17T12:12:00Z",
    "from": {
      "user_id": "usr_example_001",
      "username": "test.user"
    }
  }
}

Example response:

{
  "status": "accepted"
}
GET /stats

Returns delivery statistics.

Example:

{
  "sent": 1,
  "failed": 0,
  "queued": 0,
  "duplicates_blocked": 0
}
Event Processing Flow
A comment.created event is received through /webhook.
The event ID is checked against previously processed events.
Duplicate events are ignored.
Configured keyword rules are loaded.
The comment text is checked against each rule using case-insensitive matching.
A matching rule creates a delivery record.
Duplicate delivery for the same rule and user is prevented.
The delivery is placed into the background worker queue.
The worker sends the DM through the Pseudogram API.
Delivery status and DM ID are stored.
Temporary failures and rate limits are retried.
Statistics are exposed through /stats.
Duplicate Protection

The system uses multiple levels of duplicate protection.

Event-level deduplication

Each webhook event contains an event_id.

Processed event IDs are stored in the database so that the same event is not processed repeatedly.

Delivery-level protection

A delivery is uniquely associated with:

rule_id + user_id

A database uniqueness constraint prevents the same user from receiving the same rule's DM more than once.

Idempotency

The DM request uses an idempotency key based on:

rule_id:user_id

This provides an additional protection when communicating with the external DM API.

Background Worker

DM delivery is handled asynchronously using a Python background worker and an in-process queue.

The worker:

Retrieves queued deliveries
Checks the delivery status
Increments the attempt count
Sends the DM through the external API
Stores the returned DM ID
Updates the delivery status
Handles temporary failures
Handles rate limiting
Stops after the maximum retry count

The maximum number of attempts is:

5
Retry Handling

The system handles several API responses.

HTTP 202

The DM request is accepted and the delivery is recorded as successful/accepted.

HTTP 400

The request is considered invalid and is marked as failed without retrying.

HTTP 429

The system reads the Retry-After response header, waits for the specified period, and places the delivery back into the queue.

Other errors

Temporary errors are retried after a delay until the maximum attempt count is reached.

Running Locally
1. Create a virtual environment
python -m venv venv
2. Activate the environment

Windows PowerShell:

.\venv\Scripts\Activate.ps1
3. Install dependencies
pip install -r requirements.txt
4. Configure the API key

Create a .env file:

PSEUDOGRAM_API_KEY=your_api_key

Do not commit the .env file to GitHub.

5. Start the application
uvicorn app.main:app --reload

The local API will be available at:

http://127.0.0.1:8000

Swagger API documentation:

http://127.0.0.1:8000/docs
Docker

The application includes a Dockerfile for deployment.

The container:

Uses Python 3.11
Installs dependencies from requirements.txt
Copies the application source
Exposes port 8000
Starts the FastAPI application using Uvicorn
Deployment

The application is deployed as a Docker web service on Render.

Working URL

https://linkplease-assignment-l7ky.onrender.com

GitHub Repository

https://github.com/jyothikagunta/linkplease-assignment

API Documentation

https://linkplease-assignment-l7ky.onrender.com/docs

Statistics

https://linkplease-assignment-l7ky.onrender.com/stats

Deployment Verification

The deployed application was tested end-to-end.

A keyword rule was created and a matching comment.created event was sent to the deployed webhook.

The delivery was successfully processed by the background worker.

The deployed statistics endpoint returned:

{
  "sent": 1,
  "failed": 0,
  "queued": 0,
  "duplicates_blocked": 0
}

This confirmed a successful end-to-end delivery in the deployed environment.

Loom Demonstration

A short technical walkthrough of the implementation is available here:

https://www.loom.com/share/37606450decc4d83abe548f97320dbd2

The demonstration covers:

Webhook processing
Keyword matching
Duplicate protection
Background delivery
Retry handling
Architectural tradeoffs
Known limitations
Deployed statistics
Known Limitations

Known failure scenarios and limitations are documented in FAILURES.md.

The main architectural tradeoff is the use of an in-process background queue.

Because the queue exists in application memory, a pending job can be lost if the application process restarts before that job is processed.

A persistent external job queue would provide stronger durability for production use.

Future Improvements

With additional development time, the following improvements could be made:

Replace the in-process queue with a persistent job queue
Persist retry scheduling information
Add comprehensive automated tests
Test concurrent webhook events
Perform large-scale load testing
Improve structured logging
Add monitoring and alerting
Improve production database configuration
Assignment Completion

Parts Completed: A+B

GitHub Repository:

https://github.com/jyothikagunta/linkplease-assignment

Working URL:

https://linkplease-assignment-l7ky.onrender.com

Loom Demonstration:

https://www.loom.com/share/37606450decc4d83abe548f97320dbd2