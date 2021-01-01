from telegram import Update, ParseMode
from telegram.ext import CallbackContext, MessageHandler, CommandHandler, ConversationHandler, Filters
from tools import Tools
from keyboards import menu_kb, back_to_menu_button
from random import choice
from filters import new_user_filter
from .texts import main_menu_texts, welcome_text


def new_user_callback(update: Update, context: CallbackContext):
    uid = update.effective_chat.id
    uname = update.effective_user.username

    Tools.create_user(username=uname,
                      uid=uid)

    context.bot.send_message(chat_id=uid,
                             text=welcome_text,
                             parse_mode=ParseMode.HTML)

    menu_callback(update, context)

    return ConversationHandler.END


def menu_callback(update: Update, context: CallbackContext):

    uid = Tools.get_uid(update)

    phrase = choice(main_menu_texts)

    to_delete = context.chat_data.get('messages_to_delete', [])

    if to_delete:
        for msg in to_delete:
            try:
                context.bot.delete_message(
                    chat_id=uid,
                    message_id=msg
                )
            except:
                logger.exception(f"An error occured trying to delete message {msg} for user {uid}.")

    context.chat_data['messages_to_delete'] = []

    context.bot.send_message(chat_id=uid,
                             text=phrase,
                             parse_mode=ParseMode.HTML,
                             reply_markup=menu_kb)

    return ConversationHandler.END


new_user_handler = CommandHandler('start',
                                  filters=new_user_filter,
                                  callback=new_user_callback)

menu_handler = CommandHandler(command=['menu', 'start'],
                              callback=menu_callback,
                              pass_chat_data=True)

back_to_menu_handler = MessageHandler(Filters.regex('^{}'.format(back_to_menu_button)),
                                      callback=menu_callback)
