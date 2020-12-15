import logging
from telegram import Update
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)
from app.orm import crud, schemas

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
WAITING_SELECT_ENTITY_TO_CHANGE, \
WAITING_TYPE_NEW_QUESTION, \
WAITING_TYPE_NEW_ANSWER, \
    = range(5)

# select_endpoints = ['Назад', 'Выход']
question_answer_selector = ['Вопрос', 'Ответ']


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


def waiting_select_entity_endpoint(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Выбери что хочешь поменять",
        reply_markup=list_into_kbd(['Вопрос', 'Ответ', 'Назад', 'Выход']),
    )
    return WAITING_SELECT_ENTITY_TO_CHANGE


def start_edit(update: Update, context: CallbackContext) -> int:
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
        context.user_data['question'] = item.question
        return waiting_select_entity_endpoint(update, context)
    else:
        update.message.reply_text(f"Вопроса '{user_answer}' в карточке {card_name} нет!")
        return waiting_select_question_endpoint(update, context, card_questions_list)


def waiting_change_question_endpoint(update: Update, context: CallbackContext):
    update.message.reply_text("Введи новый вопрос:")
    return WAITING_TYPE_NEW_QUESTION


def waiting_change_answer_endpoint(update: Update, context: CallbackContext):
    update.message.reply_text("Введи новый ответ:")
    return WAITING_TYPE_NEW_ANSWER


def change_answer(update: Update, context: CallbackContext):
    db = next(get_db())
    telegram_id = update.effective_chat.username
    card_name = context.user_data['card_name']
    question = context.user_data['question']
    new_answer = update.message.text

    crud.delete_item(db, telegram_id, card_name, question)
    new_item = schemas.ItemBase(question=question, answer=new_answer)
    item = crud.create_card_item(db, new_item, telegram_id, card_name)

    update.message.reply_text("Ответ изменен!!!")
    print_question_and_answer(update, item)

    card_questions_list = list_card_questions(db, telegram_id, card_name)
    return waiting_select_question_endpoint(update, context, card_questions_list)


def change_question(update: Update, context: CallbackContext):
    db = next(get_db())
    telegram_id = update.effective_chat.username
    card_name = context.user_data['card_name']
    question = context.user_data['question']
    new_question = update.message.text

    card_questions_list = list_card_questions(db, telegram_id, card_name)
    if new_question not in card_questions_list:
        answer = crud.get_item_for_user_card(db, telegram_id, card_name, question).answer
        crud.delete_item(db, telegram_id, card_name, question)
        new_item = schemas.ItemBase(question=new_question, answer=answer)
        item = crud.create_card_item(db, new_item, telegram_id, card_name)

        update.message.reply_text("Вопрос изменен!!!")
        print_question_and_answer(update, item)

        card_questions_list = list_card_questions(db, telegram_id, card_name)
        return waiting_select_question_endpoint(update, context, card_questions_list)
    else:
        update.message.reply_text(f"Ткой вопрос уже есть в карточке {card_name}!")
        return waiting_select_question_endpoint(update, context, card_questions_list)


def changing_item(update: Update, context: CallbackContext) -> int:
    db = next(get_db())
    telegram_id = update.effective_chat.username
    card_name = context.user_data['card_name']
    question = context.user_data['question']
    user_answer = update.message.text

    card_questions_list = list_card_questions(db, telegram_id, card_name)
    if user_answer == 'Назад':
        return waiting_select_question_endpoint(update, context, card_questions_list)

    if user_answer == 'Вопрос':
        return waiting_change_question_endpoint(update, context)

    if user_answer == 'Ответ':
        return waiting_change_answer_endpoint(update, context)


conv_handler = ConversationHandler(
    entry_points=[CommandHandler('edit', start_edit)],
    states={
        WAITING_SELECT_CARD: [
            MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Выход$')), select_card)
        ],
        WAITING_SELECT_QUESTION: [
            MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Выход$')), select_question)
        ],
        WAITING_SELECT_ENTITY_TO_CHANGE: [
            MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Выход$')), changing_item)
        ],
        WAITING_TYPE_NEW_QUESTION: [
            MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Выход$')), change_question)
        ],
        WAITING_TYPE_NEW_ANSWER: [
            MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Выход$')), change_answer)
        ],
    },
    fallbacks=[MessageHandler(Filters.regex('^Выход$'), done)],
)
