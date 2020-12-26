from telegram import Update, ParseMode
from telegram.ext import CallbackContext, MessageHandler, ConversationHandler, Filters
from tools import Tools
from keyboards import menu_keyboard, back_to_menu_kb
from .texts import settings_header, come_back_later_text
from main_screen.handlers import menu_handler, back_to_menu_handler

VIEWING_SETTINGS = range(1)


def settings_menu_callback(update: Update, context: CallbackContext):

    uid = Tools.get_uid(update)

    context.bot.send_message(chat_id=uid,
                             text=settings_header,
                             parse_mode=ParseMode.HTML,
                             reply_markup=back_to_menu_kb)

    context.bot.send_message(chat_id=uid,
                             text=come_back_later_text,
                             parse_mode=ParseMode.HTML)

    return VIEWING_SETTINGS


settings_menu_handler = MessageHandler(Filters.regex('^{}'.format(menu_keyboard[1][0])),
                                       callback=settings_menu_callback)


settings_conversation_handler = ConversationHandler(

    entry_points=[settings_menu_handler],

    states={

        VIEWING_SETTINGS: [
            back_to_menu_handler
        ]

    },

    fallbacks=[menu_handler],
    name='Settings',
    persistent=True
)
