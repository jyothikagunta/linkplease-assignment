from fastapi import APIRouter, BackgroundTasks
from sqlalchemy.exc import IntegrityError

from app.database import SessionLocal
from app.models import ProcessedEvent, Rule, Delivery
from workers.dm_worker import queue_delivery


router = APIRouter()


def process_comment(event):

    db = SessionLocal()

    try:

        event_id = event["event_id"]
        event_type = event["event_type"]

        # We only need created comments for Part A.
        if event_type != "comment.created":
            return

        data = event["data"]

        comment_id = data["comment_id"]
        text = data["text"]
        user_id = data["from"]["user_id"]

        # ---------------------------------------
        # 1. EVENT DEDUPLICATION
        # ---------------------------------------

        existing_event = (
            db.query(ProcessedEvent)
            .filter(
                ProcessedEvent.event_id == event_id
            )
            .first()
        )

        if existing_event:
            return

        processed_event = ProcessedEvent(
            event_id=event_id
        )

        db.add(processed_event)

        try:
            db.commit()

        except IntegrityError:

            # Another request inserted the same event.
            db.rollback()
            return

        # ---------------------------------------
        # 2. FIND MATCHING RULES
        # ---------------------------------------

        rules = db.query(Rule).all()

        for rule in rules:

            if rule.keyword.lower() not in text.lower():
                continue

            # ---------------------------------------
            # 3. DUPLICATE DM PROTECTION
            # ---------------------------------------

            existing_delivery = (
                db.query(Delivery)
                .filter(
                    Delivery.rule_id == rule.rule_id,
                    Delivery.user_id == user_id
                )
                .first()
            )

            if existing_delivery:
                continue

            # ---------------------------------------
            # 4. CREATE DURABLE DELIVERY
            # ---------------------------------------

            delivery = Delivery(
                rule_id=rule.rule_id,
                user_id=user_id,
                comment_id=comment_id,
                status="queued",
                attempts=0
            )

            db.add(delivery)

            try:
                db.commit()

            except IntegrityError:

                # Another event created this delivery.
                db.rollback()
                continue

            delivery_id = delivery.id

            # ---------------------------------------
            # 5. ADD TO BACKGROUND QUEUE
            # ---------------------------------------

            queue_delivery(delivery_id)

    finally:
        db.close()


@router.post("/webhook")
def webhook(
    event: dict,
    background_tasks: BackgroundTasks
):

    background_tasks.add_task(
        process_comment,
        event
    )

    return {
        "status": "accepted"
    }