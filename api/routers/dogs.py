from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api.models import Dog
from api.dependencies.deps import db_dependency, user_dependency

class DogCreateRequest(BaseModel):
    name: str
    breed: str
    age: int

router = APIRouter(
    prefix='/dogs',
    tags=['Dogs']
)

@router.get("/userdogs")
def read_dog(db: db_dependency, user: user_dependency):
    dogs = db.query(Dog).filter(Dog.user_id == user.get('id')).all()
    if dogs is None:
        raise HTTPException(status_code=404, detail="Dog not found")
    return dogs

@router.get("/{user_id}")
def read_dog(user_id: int, db: db_dependency, user: user_dependency):
    dogs = db.query(Dog).filter(Dog.user_id == user_id).all()
    if dogs is None:
        raise HTTPException(status_code=404, detail="Dog not found")
    return dogs

@router.post("/")
def create_dog(db: db_dependency, user: user_dependency, dog: DogCreateRequest):
    db_dog = Dog(**dog.model_dump())
    db_dog.user_id = user.get('id')
    db.add(db_dog)
    db.commit()
    db.refresh(db_dog)
    return db_dog.id

@router.delete("/{dog_id}")
def delete_dog(db: db_dependency, user: user_dependency, dog_id: int):
    dog = db.query(Dog).filter(Dog.id == dog_id).filter(Dog.user_id == user.get('id')).first()
    if dog is None:
        raise HTTPException(status_code=404, detail="Dog not found")
    db.delete(dog)
    db.commit()
    return {"msg": "Dog deleted"}