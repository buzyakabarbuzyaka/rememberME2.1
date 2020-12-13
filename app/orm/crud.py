from sqlalchemy.orm import Session

from app.orm import models, schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_telegram_id(db: Session, telegram_id: str):
    return db.query(models.User).filter(models.User.telegram_id == telegram_id).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(telegram_id=user.telegram_id)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def user_card_exists(db: Session, telegram_id: str, card_name: str):
    user_id = get_user_by_telegram_id(db=db, telegram_id=telegram_id).id
    return db.query(models.Card).filter_by(user_id=user_id).filter_by(card_name=card_name).all()


def get_cards(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Card).offset(skip).limit(limit).all()


def get_cards_for_user(db: Session, telegram_id: str, skip: int = 0, limit: int = 100):
    user_id = get_user_by_telegram_id(db=db, telegram_id=telegram_id).id
    return db.query(models.Card).filter_by(user_id=user_id).offset(skip).limit(limit).all()


def _get_cards_for_user(db: Session, telegram_id: str):
    user_id = get_user_by_telegram_id(db=db, telegram_id=telegram_id).id
    return db.query(models.Card).filter_by(user_id=user_id).all()


def create_user_card(db: Session, card: schemas.CardBase, telegram_id: str):
    user_id = get_user_by_telegram_id(db=db, telegram_id=telegram_id).id
    db_item = models.Card(**card.dict(), user_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_card_id_by_name(db: Session, telegram_id: str, card_name: str):
    user_id = get_user_by_telegram_id(db=db, telegram_id=telegram_id).id
    return db.query(models.Card).filter_by(user_id=user_id).filter_by(card_name=card_name).first()


def user_card_question_exists(db: Session, telegram_id: str, card_name: str, question: str):
    user_id = get_user_by_telegram_id(db=db, telegram_id=telegram_id).id
    card_id = get_card_id_by_name(db=db, telegram_id=telegram_id, card_name=card_name).id

    return db.query(models.Item).filter_by(card_id=card_id).filter_by(question=question).all()


def create_card_item(db: Session, item: schemas.ItemBase, telegram_id: str, card_name: str):
    user_id = get_user_by_telegram_id(db=db, telegram_id=telegram_id).id
    card_id = db.query(models.Card).filter_by(user_id=user_id, card_name=card_name).first().id
    db_item = models.Item(**item.dict(), card_id=card_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_items_for_user_card(db: Session, telegram_id: str, card_name: str, skip: int = 0, limit: int = 100):
    user_id = get_user_by_telegram_id(db=db, telegram_id=telegram_id).id
    card_id = db.query(models.Card).filter_by(user_id=user_id, card_name=card_name).first().id
    return db.query(models.Item).filter_by(card_id=card_id).offset(skip).limit(limit).all()


def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()
