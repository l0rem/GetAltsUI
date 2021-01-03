from telegram.ext import Updater, CommandHandler
from decouple import config
from main_screen.handlers import menu_handler, new_user_handler
from balance_screen.handlers import balance_conversation_handler, precheckout_handler, tgpay_success_handler
from rent_screen.handlers import rent_conversation_handler
from help_screen.handlers import help_conversation_handler
from settings_screen.handlers import settings_conversation_handler
from api_screen.handlers import api_conversation_handler
import sentry_sdk
import logging
from logdna import LogDNAHandler
from sentry_sdk.integrations.logging import LoggingIntegration

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(message)s')

logDNAoptions = dict()
logDNAoptions['index_meta'] = True
logDNAoptions['hostname'] = config('HOSTNAME', default='localhost')
logDNAhandler = LogDNAHandler(config('LOGDNA_KEY'), options=logDNAoptions)

logger = logging.getLogger()
logger.addHandler(logDNAhandler)

sentry_logging = LoggingIntegration(
    level=logging.DEBUG,
    event_level=logging.ERROR
)

sentry_sdk.init(
    config('SENTRY_URL'),
    traces_sample_rate=1.0,
    integrations=[sentry_logging]
)


class GetAltsBot:
    def __init__(self, token: str):
        self.__api_token = token
        self.updater = Updater(token=self.__api_token)
        self.dispatcher = self.updater.dispatcher
        self.job_q = self.updater.job_queue


if __name__ == '__main__':
    env = config('ENV', default='DEBUG')

    if env == 'DEBUG':
        bot = GetAltsBot(config('BOT_TEST_TOKEN'))
    elif env == 'PRODUCTION':
        bot = GetAltsBot(config('BOT_TOKEN'))
    else:
        raise EnvironmentError

    bot.dispatcher.add_handler(CommandHandler("debug", lambda u, _: u.message.reply_text("I'm up!")), group=-666)
    bot.dispatcher.add_handler(new_user_handler)
    bot.dispatcher.add_handler(balance_conversation_handler)
    bot.dispatcher.add_handler(rent_conversation_handler)
    bot.dispatcher.add_handler(help_conversation_handler)
    bot.dispatcher.add_handler(settings_conversation_handler)
    bot.dispatcher.add_handler(api_conversation_handler)
    bot.dispatcher.add_handler(menu_handler)
    bot.dispatcher.add_handler(precheckout_handler)
    bot.dispatcher.add_handler(tgpay_success_handler)
    bot.updater.start_polling()
    bot.updater.idle()
