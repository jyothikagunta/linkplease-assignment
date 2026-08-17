import time
import threading
from queue import Queue

from app.database import SessionLocal
from app.models import Delivery, Rule
from services.mock_api import send_dm, get_dm_status


job_queue = Queue()

# Maximum allowed by PseudoGram is 10 requests per rolling 60 seconds.
# One request every 6 seconds keeps us safely below that limit.
REQUEST_INTERVAL = 6

MAX_RETRIES = 5


def queue_delivery(delivery_id):
    job_queue.put(delivery_id)


def process_delivery(delivery_id):

    db = SessionLocal()

    try:
        delivery = (
            db.query(Delivery)
            .filter(Delivery.id == delivery_id)
            .first()
        )

        if not delivery:
            return

        # Already permanently delivered.
        if delivery.status == "delivered":
            return

        # If this delivery has failed too many times, stop retrying.
        if delivery.attempts >= MAX_RETRIES:
            delivery.status = "failed"
            db.commit()
            return

        rule = (
            db.query(Rule)
            .filter(Rule.rule_id == delivery.rule_id)
            .first()
        )

        if not rule:
            delivery.status = "failed"
            db.commit()
            return

        delivery.attempts += 1
        db.commit()

        try:
            response = send_dm(
                recipient_user_id=delivery.user_id,
                message=rule.dm_message,
                comment_id=delivery.comment_id,
                idempotency_key=f"{delivery.rule_id}:{delivery.user_id}"
            )

            # -----------------------------------
            # DM accepted by PseudoGram
            # -----------------------------------

            if response.status_code in (200, 202):

                result = response.json()

                delivery.dm_id = result["dm_id"]
                delivery.status = "accepted"

                db.commit()

                # Check the eventual delivery result.
                check_delivery_status(delivery.id)

            # -----------------------------------
            # Rate limited
            # -----------------------------------

            elif response.status_code == 429:

                delivery.status = "queued"
                db.commit()

                retry_after = response.headers.get(
                    "Retry-After",
                    "10"
                )

                try:
                    wait_time = int(retry_after)
                except ValueError:
                    wait_time = 10

                time.sleep(wait_time)

                queue_delivery(delivery.id)

            # -----------------------------------
            # Invalid request - don't retry
            # -----------------------------------

            elif response.status_code == 400:

                delivery.status = "failed"
                db.commit()

            # -----------------------------------
            # Server error - retry
            # -----------------------------------

            elif response.status_code >= 500:

                delivery.status = "queued"
                db.commit()

                time.sleep(5)

                queue_delivery(delivery.id)

            else:

                delivery.status = "queued"
                db.commit()

                time.sleep(5)

                queue_delivery(delivery.id)

        except Exception as error:

            print(
                f"DM request failed for delivery "
                f"{delivery.id}: {error}"
            )

            delivery.status = "queued"
            db.commit()

            time.sleep(5)

            queue_delivery(delivery.id)

    finally:
        db.close()


def check_delivery_status(delivery_id):

    db = SessionLocal()

    try:

        delivery = (
            db.query(Delivery)
            .filter(Delivery.id == delivery_id)
            .first()
        )

        if not delivery or not delivery.dm_id:
            return

        try:

            response = get_dm_status(delivery.dm_id)

            if response.status_code != 200:
                return

            result = response.json()

            status = result.get("status")

            # -------------------------------
            # Successfully delivered
            # -------------------------------

            if status == "delivered":

                delivery.status = "delivered"
                db.commit()

                print(
                    f"DM delivered successfully: "
                    f"{delivery.dm_id}"
                )

            # -------------------------------
            # Permanently failed
            # -------------------------------

            elif status == "failed":

                if delivery.attempts >= MAX_RETRIES:

                    delivery.status = "failed"
                    db.commit()

                    print(
                        f"DM permanently failed: "
                        f"{delivery.dm_id}"
                    )

                else:

                    delivery.status = "queued"
                    db.commit()

                    time.sleep(5)

                    queue_delivery(delivery.id)

            # -------------------------------
            # Still queued
            # -------------------------------

            elif status == "queued":

                delivery.status = "accepted"
                db.commit()

                time.sleep(5)

                queue_delivery(delivery.id)

        except Exception as error:

            print(
                f"Could not check DM status "
                f"{delivery.dm_id}: {error}"
            )

    finally:
        db.close()


def worker_loop():

    while True:

        delivery_id = job_queue.get()

        try:
            process_delivery(delivery_id)

        finally:
            job_queue.task_done()

        # Keep us safely below the API rate limit.
        time.sleep(REQUEST_INTERVAL)


def start_worker():

    worker = threading.Thread(
        target=worker_loop,
        daemon=True
    )

    worker.start()

    print("DM worker started")