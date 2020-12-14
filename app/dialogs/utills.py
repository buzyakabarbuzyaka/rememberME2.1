from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ConversationHandler,
    CallbackContext,
)
from app.orm import crud, schemas, models
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


def list_into_kbd(buttons_list):
    double_list = [[button] for button in buttons_list]
    return ReplyKeyboardMarkup(double_list, one_time_keyboard=True)


def no_cards_endpoint(update: Update, context: CallbackContext):
    update.message.reply_text("У тебя пока нету карточек(")
    return ConversationHandler.END


def register(update: Update, context: CallbackContext):
    db = next(get_db())
    telegram_id = update.effective_chat.username
    db_user = crud.get_user_by_telegram_id(db, telegram_id=telegram_id)

    if not db_user:
        update.message.reply_text("Ты новенький. Зарегистрировал тебя!)")
        user = schemas.UserCreate(telegram_id=telegram_id)
        crud.create_user(db=db, user=user)
        return True
    else:
        update.message.reply_text("Снова здарова")
        return False


def done(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('---End---')
    context.user_data.clear()
    return ConversationHandler.END


def print_question_and_answer(update: Update, item: models.Item):
    update.message.reply_text(f"Вопрос: {item.question}")
    update.message.reply_text(f"Ответ: {item.answer}")


def list_card_questions(db, telegram_id, card_name):
    query_items = crud._get_items_for_user_card(db, telegram_id, card_name)
    return [item.question for item in query_items]
