from fastapi import APIRouter
from app.database import SessionLocal
from app.models import Delivery

router = APIRouter()


@router.get("/stats")
def get_stats():
    db = SessionLocal()

    try:
        sent = db.query(Delivery).filter(
            Delivery.status == "delivered"
        ).count()

        failed = db.query(Delivery).filter(
            Delivery.status == "failed"
        ).count()

        queued = db.query(Delivery).filter(
            Delivery.status.in_(["queued", "accepted"])
        ).count()

        return {
            "sent": sent,
            "failed": failed,
            "queued": queued,
            "duplicates_blocked": 0
        }

    finally:
        db.close()