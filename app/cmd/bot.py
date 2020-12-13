import logging
import telegram
import collections
from telegram.ext import Filters, Updater, MessageHandler, CommandHandler
from app.settings import TOKEN

from app.orm import models, crud, schemas
from app.orm.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

bot = telegram.Bot(TOKEN)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def remember():
    answer = yield "Я слушаю)"
    buffer[answer.from_user.id] = answer.text
    return answer.text


handlers = collections.defaultdict(remember)
buffer = collections.defaultdict(lambda: 'empty')


def remember_handler(update, context):
    print(f'{update.message.from_user.username}:{update.message.text}')
    print("remember")
    telegram_id = update.message.from_user.id

    answer = next(handlers[telegram_id])
    # отправляем полученный ответ пользователю
    bot.send_message(chat_id=telegram_id, text=answer)


def insult(update, context):
    print(f'{update.message.from_user.username}:{update.message.text}')
    telegram_id = update.message.from_user.id
    if telegram_id in handlers:
        # если диалог уже начат, то надо использовать .send(), чтобы
        # передать в генератор ответ пользователя
        try:
            handlers[telegram_id].send(update.message)
        except StopIteration:
            del handlers[telegram_id]
            bot.send_message(chat_id=telegram_id, text=buffer[telegram_id])
            del buffer[telegram_id]
            bot.send_message(chat_id=telegram_id, text="Я канеш запомнил, но ты все равно идешь нахуй.")
            return

    update.message.reply_text('Ди на хуй')


def start():
    updater = Updater(TOKEN, use_context=True)
    updater.dispatcher.add_handler(CommandHandler('remember', remember_handler))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, insult))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    start()
