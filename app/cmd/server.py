import uvicorn
from typing import List
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.orm import models, crud, schemas
from app.orm.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db=db, skip=skip, limit=limit)
    return users


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_telegram_id(db, telegram_id=user.telegram_id)
    if db_user:  # TODO: Logics if user exists
        raise HTTPException(status_code=400, detail="User already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/{telegram_id}", response_model=schemas.User)
def read_user(telegram_id: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_telegram_id(db=db, telegram_id=telegram_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.get("/cards/", response_model=List[schemas.Card])
def read_all_cards(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    cards = crud.get_cards(db=db, skip=skip, limit=limit)
    return cards


@app.get("/users/{telegram_id}/cards/", response_model=List[schemas.Card])
def read_cards_for_user(telegram_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    cards = crud.get_cards_for_user(db=db, skip=skip, limit=limit, telegram_id=telegram_id)
    return cards


@app.post("/users/{telegram_id}/cards/", response_model=schemas.Card)
def create_card_for_user(
    telegram_id: str, card: schemas.CardBase, db: Session = Depends(get_db)
):
    return crud.create_user_card(db=db, card=card, telegram_id=telegram_id)


@app.get("/items/", response_model=List[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items


@app.get("/users/{telegram_id}/cards/{card_name}/items", response_model=List[schemas.Item])
def read_items_for_user(
    telegram_id: str, card_name: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    return crud.get_items_for_user_card(db=db, skip=skip, limit=limit, telegram_id=telegram_id, card_name=card_name)


@app.post("/users/{telegram_id}/cards/{card_name}/items", response_model=schemas.Item)
def create_item_for_user(
    telegram_id: str, card_name: str, item: schemas.ItemBase, db: Session = Depends(get_db)
):
    return crud.create_card_item(db=db, item=item, telegram_id=telegram_id, card_name=card_name)


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
