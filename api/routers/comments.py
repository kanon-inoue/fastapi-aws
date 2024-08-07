from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime, timezone

from api.models import Comment
from api.dependencies.deps import db_dependency, user_dependency

class CommentCreateRequest(BaseModel):
    content: str
    post_id: int

router = APIRouter(
    prefix='/comments',
    tags=['Comments']
)

@router.post("/")
def create_comment(db: db_dependency, user: user_dependency, comment: CommentCreateRequest):
    db_comment = Comment(**comment.model_dump())
    db_comment.timestamp=datetime.now(timezone.utc)
    db_comment.user_id = user.get('id')
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment