from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, validates
from datetime import datetime, timezone
from dotenv import load_dotenv
import os

load_dotenv()

Base = declarative_base()

if os.getenv("DEPLOYMENT_ENVIRONMENT") == 'DEV':
    engine = create_engine(os.getenv("DB_URL"), connect_args={'check_same_thread': False})
else:
    engine = create_engine(os.getenv("DB_URL"))

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    dogs = relationship("Dog", back_populates="owner")
    posts = relationship("Post", back_populates="user")
    images = relationship("Image", back_populates="owner", uselist=False)
    
class Image(Base):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True, index=True)
    image = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship("User", back_populates="images")

class Dog(Base):
    __tablename__ = 'dogs'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    breed = Column(String)
    age = Column(Integer)
    user_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship("User", back_populates="dogs")

class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc))
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", order_by="Comment.id")

class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc))
    user_id = Column(Integer, ForeignKey('users.id'))
    post_id = Column(Integer, ForeignKey('posts.id'))
    user = relationship("User")
    post = relationship("Post", back_populates="comments")

Base.metadata.create_all(bind=engine)
