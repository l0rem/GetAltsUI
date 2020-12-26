from telegram import Update, ParseMode, ReplyKeyboardMarkup
from telegram.ext import CallbackContext, MessageHandler, ConversationHandler, Filters
from tools import Tools
from keyboards import menu_keyboard, back_to_menu_button, back_button, topup_button, topup_options
from .texts import balance_form, balance_header
from main_screen.handlers import menu_handler, back_to_menu_handler

VIEWING_BALANCE = range(1)


def balance_callback(update: Update, context: CallbackContext):

    uid = Tools.get_uid(update)

    user = Tools.get_user(uid)

    user_balance = Tools.get_balance(user)

    balance_kb = ReplyKeyboardMarkup([[topup_button],
                                      [back_to_menu_button]])

    context.bot.send_message(chat_id=uid,
                             text=balance_header,
                             parse_mode=ParseMode.HTML,
                             reply_markup=balance_kb)

    context.bot.send_message(chat_id=uid,
                             text=balance_form.format(user_balance),
                             parse_mode=ParseMode.HTML)

    return VIEWING_BALANCE


balance_handler = MessageHandler(Filters.regex('^{}'.format(menu_keyboard[0][1])),
                                 callback=balance_callback)


def top_up_menu_callback(update: Update, context: CallbackContext):

    uid = Tools.get_uid(update)

    top_up_options_kb = ReplyKeyboardMarkup([[topup_options[0]],
                                             [back_button]])

    text = '<b>Please, choose one of the following payment methods:</b>'

    context.bot.send_message(chat_id=uid,
                             text=text,
                             parse_mode=ParseMode.HTML,
                             reply_markup=top_up_options_kb)

    return VIEWING_BALANCE


top_up_menu_handler = MessageHandler(Filters.regex('^{}'.format(topup_button)),
                                     callback=top_up_menu_callback)

back_to_balance_menu_handler = MessageHandler(Filters.regex('^{}'.format(back_button)),
                                              callback=balance_callback)


balance_conversation_handler = ConversationHandler(

    entry_points=[balance_handler],

    states={

        VIEWING_BALANCE: [
            back_to_menu_handler,

            top_up_menu_handler,

            back_to_balance_menu_handler


        ]

    },

    fallbacks=[menu_handler],
    name='Balance',
    persistent=True
)
