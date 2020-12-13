import logging
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)
from app.orm import models, crud, schemas
from app.orm.database import SessionLocal, engine


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

CARD_DELETE_CHOICE, \
WAITING_DELETE_DECISION, \
WAITING_CONTINUE, \
    = range(3)

end_deleting_items_kbd = [["Продолжить", "Завершить"]]

end_deleting_items = ReplyKeyboardMarkup(end_deleting_items_kbd, one_time_keyboard=True)


def list_card_names(db, telegram_id):
    dbs_card_list = crud._get_cards_for_user(db=db, telegram_id=telegram_id)
    return [card.card_name for card in dbs_card_list]


def make_card_names_kbd(card_names_list):
    return [[card] for card in card_names_list] + [["Выход"]]


def card_delete_endpoint(update: Update, context: CallbackContext):
    db = next(get_db())
    telegram_id = update.effective_chat.username

    card_names_list = list_card_names(db, telegram_id)
    card_names_kbd = make_card_names_kbd(card_names_list)
    card_names = ReplyKeyboardMarkup(card_names_kbd, one_time_keyboard=True)
    update.message.reply_text(
        "!!!УДАЛЕНИЕ КАРТОЧКИ!!!",
        reply_markup=card_names,
    )
    return WAITING_DELETE_DECISION


def no_cards_endpoint(update: Update, context: CallbackContext):
    update.message.reply_text("У тебя пока нету карточек(")
    return ConversationHandler.END


def start_delete(update: Update, context: CallbackContext) -> int:
    db = next(get_db())
    telegram_id = update.effective_chat.username
    db_user = crud.get_user_by_telegram_id(db, telegram_id=telegram_id)

    if not db_user:
        update.message.reply_text("Ты новенький. Зарегистрировал тебя!)")
        user = schemas.UserCreate(telegram_id=telegram_id)
        crud.create_user(db=db, user=user)
        return no_cards_endpoint(update, context)
    else:
        update.message.reply_text("Снова здарова")
        card_names_list = list_card_names(db, telegram_id)
        if not card_names_list:
            return no_cards_endpoint(update, context)
        else:
            return card_delete_endpoint(update, context)


def delete_card(update: Update, context: CallbackContext):
    db = next(get_db())
    telegram_id = update.effective_chat.username
    card_name = update.message.text

    card_exists_query = crud.user_card_exists(db=db, telegram_id=telegram_id, card_name=card_name)
    if not card_exists_query:
        update.message.reply_text(f"Карточки {card_name} нет!")

        return card_delete_endpoint(update, context)

    else:
        update.message.reply_text(f"Удаляю {card_name}:")
        crud.delete_card(db=db, card_name=card_name, telegram_id=telegram_id)
        if not list_card_names(db=db, telegram_id=telegram_id):
            return no_cards_endpoint(update, context)

        update.message.reply_text(
            "Продолжить удаление?",
            reply_markup=end_deleting_items,
        )
        return WAITING_CONTINUE


def continue_decision(update: Update, context: CallbackContext):
    reply = update.message.text

    if reply == "Продолжить":
        return card_delete_endpoint(update, context)

    if reply == "Завершить":
        return ConversationHandler.END


def done(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('---End---')
    context.user_data.clear()
    return ConversationHandler.END


conv_handler = ConversationHandler(
    entry_points=[CommandHandler('delete', start_delete)],
    states={
        WAITING_DELETE_DECISION: [
            MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Выход$')), delete_card)
        ],
        WAITING_CONTINUE: [
            MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Выход$')), continue_decision)
        ],
    },
    fallbacks=[MessageHandler(Filters.regex('^Выход$'), done)],
)
