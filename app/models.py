from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint
from datetime import datetime

from app.database import Base


class Rule(Base):
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, index=True)

    rule_id = Column(String, unique=True, index=True, nullable=False)

    keyword = Column(String, nullable=False)

    dm_message = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)


class ProcessedEvent(Base):
    __tablename__ = "processed_events"

    id = Column(Integer, primary_key=True, index=True)

    event_id = Column(String, unique=True, index=True, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)


class Delivery(Base):
    __tablename__ = "deliveries"

    id = Column(Integer, primary_key=True, index=True)

    rule_id = Column(String, nullable=False)

    user_id = Column(String, nullable=False)

    comment_id = Column(String, nullable=False)

    dm_id = Column(String, nullable=True)

    status = Column(String, nullable=False, default="queued")

    attempts = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    __table_args__ = (
        UniqueConstraint(
            "rule_id",
            "user_id",
            name="unique_rule_user"
        ),
    )