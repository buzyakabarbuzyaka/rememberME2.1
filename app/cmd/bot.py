from app.settings import TOKEN
import logging

from telegram.ext import Updater
from app.dialogs import new, delete, view, edit, play


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def main() -> None:
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(new.conv_handler)
    dispatcher.add_handler(delete.conv_handler)
    dispatcher.add_handler(view.conv_handler)
    dispatcher.add_handler(edit.conv_handler)
    dispatcher.add_handler(play.conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
