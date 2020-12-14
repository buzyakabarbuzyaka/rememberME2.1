import logging
from telegram import Update
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)
from app.orm import crud

from app.dialogs.utills import (
    get_db,
    list_card_names,
    no_cards_endpoint,
    register,
    list_into_kbd,
    list_card_questions,
    print_question_and_answer,
    done,
)

logger = logging.getLogger(__name__)

WAITING_SELECT_CARD, \
WAITING_SELECT_QUESTION, \
    = range(2)

select_endpoints = ['Назад', 'Выход']


def waiting_select_card_endpoint(update: Update, context: CallbackContext, cards_name_list):
    update.message.reply_text(
        "Выбери карточку:",
        reply_markup=list_into_kbd(cards_name_list + ['Выход']),
    )
    return WAITING_SELECT_CARD


def waiting_select_question_endpoint(update: Update, context: CallbackContext, card_questions_list):
    update.message.reply_text(
        "Выбери вопрос:",
        reply_markup=list_into_kbd(card_questions_list + ['Назад', 'Выход']),
    )
    return WAITING_SELECT_QUESTION


def start_view(update: Update, context: CallbackContext) -> int:
    db = next(get_db())
    telegram_id = update.effective_chat.username

    is_already_registered = register(update, context)
    cards_name_list = list_card_names(db, telegram_id)
    if cards_name_list:
        return waiting_select_card_endpoint(update, context, cards_name_list)
    else:
        return no_cards_endpoint(update, context)


def select_card(update: Update, context: CallbackContext) -> int:
    db = next(get_db())
    telegram_id = update.effective_chat.username
    card_name = update.message.text

    cards_name_list = list_card_names(db, telegram_id)
    if card_name in cards_name_list:
        update.message.reply_text(f"Карточка с именем {card_name}:")
        context.user_data['card_name'] = card_name
        card_questions_list = list_card_questions(db, telegram_id, card_name)
        return waiting_select_question_endpoint(update, context, card_questions_list)
    else:
        update.message.reply_text(f"Карточки с именем {card_name} нет!")
        return waiting_select_card_endpoint(update, context, cards_name_list)


def select_question(update: Update, context: CallbackContext) -> int:
    db = next(get_db())
    telegram_id = update.effective_chat.username
    card_name = context.user_data['card_name']
    user_answer = update.message.text

    card_name_list = list_card_names(db, telegram_id)
    if user_answer == 'Назад':
        return waiting_select_card_endpoint(update, context, card_name_list)

    card_questions_list = list_card_questions(db, telegram_id, card_name)
    if user_answer in card_questions_list:
        question = user_answer
        item = crud.get_item_for_user_card(db=db, telegram_id=telegram_id, card_name=card_name, question=question)
        print_question_and_answer(update, item)
        return waiting_select_question_endpoint(update, context, card_questions_list)
    else:
        update.message.reply_text(f"Вопроса '{user_answer}' в карточке {card_name} нет!")
        return waiting_select_question_endpoint(update, context, card_questions_list)


conv_handler = ConversationHandler(
    entry_points=[CommandHandler('view', start_view)],
    states={
        WAITING_SELECT_CARD: [
            MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Выход$')), select_card)
        ],
        WAITING_SELECT_QUESTION: [
            MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Выход$')), select_question)
        ],
    },
    fallbacks=[MessageHandler(Filters.regex('^Выход$'), done)],
)
