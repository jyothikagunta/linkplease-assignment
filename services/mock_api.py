import os
import requests
from dotenv import load_dotenv

load_dotenv()

MOCK_API_BASE_URL = "https://pseudogram-api.onrender.com"
API_KEY = os.getenv("PSEUDOGRAM_API_KEY")


def send_dm(recipient_user_id, message, comment_id, idempotency_key):
    url = f"{MOCK_API_BASE_URL}/v1/dm/send"

    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json",
        "Idempotency-Key": idempotency_key
    }

    payload = {
        "recipient_user_id": recipient_user_id,
        "message": message,
        "comment_id": comment_id
    }

    return requests.post(
        url,
        json=payload,
        headers=headers,
        timeout=10
    )


def get_dm_status(dm_id):
    url = f"{MOCK_API_BASE_URL}/v1/dm/{dm_id}"

    headers = {
        "X-API-Key": API_KEY
    }

    return requests.get(
        url,
        headers=headers,
        timeout=10
    )