import logging
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)
from app.orm import crud, schemas

from app.dialogs.utills import get_db, list_card_names

logger = logging.getLogger(__name__)

CARD_CREATION_CHOICE, \
TYPING_NEW_CARD_NAME, \
CREATING_QUESTION, \
CREATING_ANSWER, \
ITEM_CREATION_WAITING_REPLY, \
    = range(5)

start_creation_kbd = [['Создать новую'],
                      ["Выход"]]

end_creating_items_kbd = [["Продолжить", "Завершить"]]

start_creation = ReplyKeyboardMarkup(start_creation_kbd, one_time_keyboard=True)
end_creating_items = ReplyKeyboardMarkup(end_creating_items_kbd, one_time_keyboard=True)


def start_new(update: Update, context: CallbackContext) -> int:
    db = next(get_db())
    telegram_id = update.effective_chat.username
    db_user = crud.get_user_by_telegram_id(db, telegram_id=telegram_id)

    if not db_user:
        update.message.reply_text("Ты новенький. Зарегистрировал тебя!)")
        user = schemas.UserCreate(telegram_id=telegram_id)
        crud.create_user(db=db, user=user)
    else:
        update.message.reply_text("Снова здарова")
        card_list = list_card_names(db=db, telegram_id=telegram_id)
        if card_list:
            card_list_msg = '\t- ' + '\n\t- '.join(card_list)
            update.message.reply_text(f"Уже созданные тобой карточки:\n{card_list_msg}")
        else:
            update.message.reply_text(f"Ты пока не создал ни одной карточки(\n{card_list_msg}")

    update.message.reply_text(
        "Меню создания карточки:",
        reply_markup=start_creation,
    )
    return CARD_CREATION_CHOICE


def card_creation_choice(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    update.message.reply_text(f'reply: {text.lower()}')

    if text == 'Создать новую':
        update.message.reply_text(f'Введите уникальное имя катрочки:')
        return TYPING_NEW_CARD_NAME


def new_card_name_process(update: Update, context: CallbackContext) -> int:
    db = next(get_db())
    telegram_id = update.effective_chat.username
    card_name = update.message.text

    result = crud.user_card_exists(db=db, telegram_id=telegram_id, card_name=card_name)

    if result:
        update.message.reply_text(f"Карточка {card_name} уже есть!")
        update.message.reply_text(f'Введите уникальное имя катрочки:')
        return TYPING_NEW_CARD_NAME
    else:
        update.message.reply_text(f"Создаю катрочку с именем: {card_name}")
        context.user_data['card_name'] = card_name
        context.user_data['card_item'] = dict()
        card = schemas.CardBase(card_name=card_name)
        crud.create_user_card(db=db, card=card, telegram_id=telegram_id)

        update.message.reply_text(f'Введите вопрос:')
        return CREATING_QUESTION


def creating_question(update: Update, context: CallbackContext):
    db = next(get_db())
    telegram_id = update.effective_chat.username
    card_name = context.user_data['card_name']

    question = update.message.text
    if not question:
        update.message.reply_text(f"Вопрос не может быть пустым!")
        update.message.reply_text(f'Введите вопрос:')
        return CREATING_QUESTION

    query = crud.user_card_question_exists(db=db, telegram_id=telegram_id, card_name=card_name, question=question)
    if query:
        update.message.reply_text(f"Вопрос {question} уже есть в катрочке {card_name}!")
        update.message.reply_text(f'Введите вопрос:')
        return CREATING_QUESTION
    else:
        update.message.reply_text(f"Сохраняю вопрос: {question}")
        context.user_data['card_item']['question'] = question
        update.message.reply_text(f'Введите ответ:')
        return CREATING_ANSWER


def item_creation_decision(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Продолжить?",
        reply_markup=end_creating_items,
    )
    return ITEM_CREATION_WAITING_REPLY


def list_card(update: Update, context: CallbackContext):
    update.message.reply_text(f"Залистить карточку!!!!!")
    context.user_data.clear()
    return ConversationHandler.END


def item_creation_decision_reply(update: Update, context: CallbackContext):
    reply = update.message.text
    if reply == "Продолжить":
        update.message.reply_text(f'Введите вопрос:')
        return CREATING_QUESTION

    if reply == "Завершить":
        return list_card(update, context)


def creating_answer(update: Update, context: CallbackContext):
    db = next(get_db())
    telegram_id = update.effective_chat.username
    card_name = context.user_data['card_name']
    answer = update.message.text

    if not answer:
        update.message.reply_text(f"Ответ не может быть пустым!")
        update.message.reply_text(f'Введите ответ:')
        return CREATING_ANSWER
    else:
        update.message.reply_text(f"Сохраняю ответ: {answer}")
        context.user_data['card_item']['answer'] = answer
        item = schemas.ItemBase(**context.user_data['card_item'])
        crud.create_card_item(db=db, item=item, telegram_id=telegram_id, card_name=card_name)
        context.user_data['card_item'] = dict()

        return item_creation_decision(update, context)


def done(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('---End---')
    context.user_data.clear()
    return ConversationHandler.END


conv_handler = ConversationHandler(
    entry_points=[CommandHandler('new', start_new)],
    states={
        CARD_CREATION_CHOICE: [
            MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Выход$')), card_creation_choice),
        ],
        TYPING_NEW_CARD_NAME: [
            MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Выход$')), new_card_name_process)
        ],
        CREATING_QUESTION: [
            MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Выход$')), creating_question)
        ],
        CREATING_ANSWER: [
            MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Выход$')), creating_answer)
        ],
        ITEM_CREATION_WAITING_REPLY: [
            MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Выход$')),
                           item_creation_decision_reply)
        ],
    },
    fallbacks=[MessageHandler(Filters.regex('^Выход$'), done)],
)
