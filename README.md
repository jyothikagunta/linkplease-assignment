# LinkPlease Assignment

A FastAPI-based webhook processing system that detects keyword matches in comments and sends direct messages through the Pseudogram API.

## Features

- Create keyword-based DM rules
- Receive `comment.created` webhook events
- Case-insensitive keyword matching
- Event deduplication using `event_id`
- Duplicate DM protection per rule and user
- Durable delivery records using SQLite
- Background DM worker
- Retry handling for temporary failures
- Rate-limit handling for HTTP 429 responses
- Maximum retry limit
- Delivery status tracking
- Statistics endpoint
- Docker deployment support

## Architecture

Webhook Event
    ↓
Keyword Rule Matching
    ↓
Duplicate Protection
    ↓
Delivery Record
    ↓
Background Worker
    ↓
Pseudogram DM API
    ↓
Delivery Status / Statistics

## API Endpoints

### Create Rule

`POST /rules`

Example:

```json
{
  "keyword": "OFFER",
  "dm_message": "Here is the offer information!"
}
Webhook

POST /webhook

Receives comment events and queues matching DM deliveries.

Statistics

GET /stats

Returns delivery statistics.

Example:

{
  "sent": 1,
  "failed": 0,
  "queued": 0,
  "duplicates_blocked": 0
}
Root

GET /

Returns the API status.

Technology Stack
Python
FastAPI
SQLAlchemy
SQLite
Pydantic
Uvicorn
Docker
Pseudogram API
Running Locally

Create and activate a virtual environment:

python -m venv venv

Windows PowerShell:

.\venv\Scripts\Activate.ps1

Install dependencies:

pip install -r requirements.txt

Create a .env file containing:

PSEUDOGRAM_API_KEY=your_api_key

Start the application:

uvicorn app.main:app --reload

The API will be available at:

http://127.0.0.1:8000

Swagger documentation:

http://127.0.0.1:8000/docs
Deployment

The application is deployed using Docker on Render.

Working URL:

https://linkplease-assignment-l7ky.onrender.com

Limitations

Known limitations and failure scenarios are documented in FAILURES.md.

The main architectural tradeoff is the use of an in-process background queue. Pending jobs stored only in memory can be lost if the application process restarts before they are processed.

Assignment

Parts completed:

A+B

GitHub Repository:

https://github.com/jyothikagunta/linkplease-assignment



### Important


**Don't put your actual API key anywhere in `README.md`.**


And your ZIP should contain:


```text
app/
routes/
services/
workers/
requirements.txt
Dockerfile
README.md
FAILURES.md

No .env, venv, .git, database, or API key.
