from telegram.ext import Updater, PicklePersistence
from decouple import config
import logging
from main_screen.handlers import menu_handler, new_user_handler
from balance_screen.handlers import balance_conversation_handler
from rent_screen.handlers import rent_conversation_handler
from help_screen.handlers import help_conversation_handler
from settings_screen.handlers import settings_conversation_handler
from api_screen.handlers import api_conversation_handler
from loguru import logger


class GetAltsBot:
    def __init__(self, token: str):
        self.__api_token = token
        self.pp = PicklePersistence(filename='GetAltsPP')
        self.updater = Updater(token=self.__api_token, persistence=self.pp)
        self.dispatcher = self.updater.dispatcher
        self.job_q = self.updater.job_queue


if __name__ == '__main__':

    bot = GetAltsBot(config('BOT_TOKEN'))

    bot.dispatcher.add_handler(CommandHandler("debug", lambda u, _: u.message.reply_text("I'm up!"), group=-999)
    bot.dispatcher.add_handler(new_user_handler)
    bot.dispatcher.add_handler(balance_conversation_handler)
    bot.dispatcher.add_handler(rent_conversation_handler)
    bot.dispatcher.add_handler(help_conversation_handler)
    bot.dispatcher.add_handler(settings_conversation_handler)
    bot.dispatcher.add_handler(api_conversation_handler)
    bot.dispatcher.add_handler(menu_handler)

    bot.updater.start_polling()
