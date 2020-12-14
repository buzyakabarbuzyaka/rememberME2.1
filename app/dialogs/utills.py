from telegram import Update
from telegram.ext import (
    ConversationHandler,
    CallbackContext,
)
from app.orm import crud
from app.orm.database import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def list_card_names(db, telegram_id):
    dbs_card_list = crud._get_cards_for_user(db=db, telegram_id=telegram_id)
    return [card.card_name for card in dbs_card_list]


def no_cards_endpoint(update: Update, context: CallbackContext):
    update.message.reply_text("У тебя пока нету карточек(")
    return ConversationHandler.END
