from telegram import Update, ParseMode
from telegram.ext import CallbackContext, MessageHandler, ConversationHandler, Filters
from tools import Tools
from keyboards import menu_keyboard, back_to_menu_kb
from .texts import api_header, come_back_later_text
from main_screen.handlers import menu_handler, back_to_menu_handler

VIEWING_API = range(1)


def api_menu_callback(update: Update, context: CallbackContext):

    uid = Tools.get_uid(update)

    context.bot.send_message(chat_id=uid,
                             text=api_header,
                             parse_mode=ParseMode.HTML,
                             reply_markup=back_to_menu_kb)

    context.bot.send_message(chat_id=uid,
                             text=come_back_later_text,
                             parse_mode=ParseMode.HTML)

    return VIEWING_API


api_menu_handler = MessageHandler(Filters.regex('^{}'.format(menu_keyboard[1][1])),
                                  callback=api_menu_callback)


api_conversation_handler = ConversationHandler(

    entry_points=[api_menu_handler],

    states={

        VIEWING_API: [
            back_to_menu_handler
        ]

    },

    fallbacks=[menu_handler],
    name='API',
    persistent=False
)
