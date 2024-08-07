from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import func
from typing import Optional, List
from datetime import datetime, timezone, timedelta

from api.models import Post, Comment, User, Image
from api.dependencies.deps import db_dependency, user_dependency

class PostCreateRequest(BaseModel):
    content: str

class PostUserResponse(BaseModel):
    id: int
    content: str
    time_ago: str
    user_id: int
    first_name: str  
    last_name: str 
    username: str
    comments_count: int 
    image: Optional[str] = None

class UserBase(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str
    image: Optional[str] = None

class CommentSchema(BaseModel):
    id: int
    content: str
    time_ago: str
    user_id: int
    user: UserBase

class PostSchema(BaseModel):
    id: int
    content: str
    time_ago: str
    user_id: int
    user: UserBase
    comments: List[CommentSchema] = []


router = APIRouter(
    prefix='/posts',
    tags=['Posts']
)

@router.get("/")
def read_posts(db: db_dependency, user: user_dependency, 
               page: int = Query(1, ge=1)):
    size = 10
    offset = (page - 1) * size
    posts_with_comments = db.query(
        Post,
        User.first_name,
        User.last_name,
        User.username,
        Image,
        func.count(Comment.id).label("comments_count")
    ).join(User, Post.user_id == User.id
    ).join(Image, User.id == Image.user_id
    ).outerjoin(Comment, Comment.post_id == Post.id
    ).group_by(Post.id, User.first_name, User.last_name, User.username, Image.id
    ).order_by(Post.id.desc()
    ).offset(offset
    ).limit(size 
    ).all()

    return [
        PostUserResponse(
            id=post.id,
            content=post.content,
            time_ago=return_date_time_passed(post.timestamp),
            user_id=post.user_id,
            first_name=first_name,
            last_name=last_name,
            username=username,
            image=image.image,
            comments_count=comments_count
        ) for post, first_name, last_name, username, image, comments_count in posts_with_comments
    ]

@router.get("/{post_id}", response_model=PostSchema)
def read_post_with_comments(post_id: int, db: db_dependency):
    post = db.query(Post).options(
        joinedload(Post.user),
        joinedload(Post.comments).joinedload(Comment.user)
    ).filter(Post.id == post_id).first()
    
    image = db.query(Image).filter(post.user.id == Image.user_id).first()
    post.user.image = image.image

    post.time_ago = return_date_time_passed(post.timestamp)
    post.comments.sort(key=lambda x: x.timestamp, reverse=True)

    for comment in post.comments:
        comment.time_ago=return_date_time_passed(comment.timestamp)
        comment_image = db.query(Image).filter(comment.user_id == Image.user_id).first()
        comment.user.image = comment_image.image
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return post

@router.post("/")
def create_post(db: db_dependency, user: user_dependency, post: PostCreateRequest):
    db_post = Post(content=post.content, user_id=user.get('id'), timestamp=datetime.now(timezone.utc))
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post.id

def return_date_time_passed(given_datetime):
    # Getting the current UTC datetime

    if given_datetime.tzinfo is None:
        given_datetime = given_datetime.replace(tzinfo=timezone.utc)

    current_datetime = datetime.now(timezone.utc)

    # Calculating the time difference
    time_difference = current_datetime - given_datetime

    # Converting time difference to total seconds
    total_seconds = int(time_difference.total_seconds())

    # Determine the output based on the time difference
    if total_seconds < 60:
        return "now"
    elif total_seconds < 3600:
        minutes = total_seconds // 60
        return f"{minutes}m"
    else:
        hours = total_seconds // 3600
        return f"{hours}h"
