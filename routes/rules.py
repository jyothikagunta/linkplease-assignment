from fastapi import APIRouter, status
from pydantic import BaseModel
import uuid

from app.database import SessionLocal
from app.models import Rule


router = APIRouter()


class RuleCreate(BaseModel):
    keyword: str
    dm_message: str


@router.post("/rules", status_code=status.HTTP_201_CREATED)
def create_rule(rule: RuleCreate):

    rule_id = str(uuid.uuid4())

    db = SessionLocal()

    new_rule = Rule(
        rule_id=rule_id,
        keyword=rule.keyword,
        dm_message=rule.dm_message
    )

    db.add(new_rule)
    db.commit()
    db.refresh(new_rule)

    db.close()

    return {
        "rule_id": new_rule.rule_id,
        "keyword": new_rule.keyword,
        "dm_message": new_rule.dm_message
    }