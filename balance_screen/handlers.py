from telegram import Update, ParseMode, ReplyKeyboardMarkup, ReplyKeyboardRemove, LabeledPrice, PreCheckoutQuery
from telegram.ext import CallbackContext, MessageHandler, ConversationHandler, Filters, PreCheckoutQueryHandler
from tools import Tools
from keyboards import menu_keyboard, back_to_menu_button, back_button, topup_button, topup_options
from .texts import balance_form, balance_header
from main_screen.handlers import menu_handler, back_to_menu_handler, menu_callback
from decouple import config


VIEWING_BALANCE, CHOOSING_TOPUP_OPTION, ENTERING_AMOUNT, PAYING_TGPAY = range(4)


def balance_callback(update: Update, context: CallbackContext):

    uid = Tools.get_uid(update)

    user = Tools.get_user(uid)

    user_balance = Tools.get_balance(user)

    balance_kb = ReplyKeyboardMarkup([[topup_button],
                                      [back_to_menu_button]],
                                     resize_keyboard=True)

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
                                             [back_button]],
                                            resize_keyboard=True)

    text = '<b>Please, choose one of the following payment methods:</b>'

    context.bot.send_message(chat_id=uid,
                             text=text,
                             parse_mode=ParseMode.HTML,
                             reply_markup=top_up_options_kb)

    return CHOOSING_TOPUP_OPTION


top_up_menu_handler = MessageHandler(Filters.regex('^{}'.format(topup_button)),
                                     callback=top_up_menu_callback)


def telegram_topup_callback(update: Update, context: CallbackContext):

    uid = Tools.get_uid(update)

    text = '<b>How much 💶 would you like to send?</b>\n\nNote, that only round numbers are accepted. Send /menu to ' \
           'return back to main menu.'

    context.bot.send_message(chat_id=uid,
                             text=text,
                             parse_mode=ParseMode.HTML,
                             reply_markup=ReplyKeyboardRemove())

    return ENTERING_AMOUNT


telegram_topup_handler = MessageHandler(Filters.regex('^{}'.format(topup_options[0])),
                                        callback=telegram_topup_callback)


def amount_callback(update: Update, context: CallbackContext):

    uid = Tools.get_uid(update)

    amount = update.effective_message.text

    wrong_amount_text = '<b>Sorry, but the amount You provided is not correct.</b>\n\nTry again or use /menu to return' \
                        ' to main menu.'

    if amount.isdigit() and int(amount) > 0:
        amount = int(amount)
    else:
        context.bot.send_message(chat_id=uid,
                                 text=wrong_amount_text,
                                 parse_mode=ParseMode.HTML)
        return ENTERING_AMOUNT

    title = "GetAlts Balance replenishment"
    description = "No refunds guaranteed, but we are nice people, so just text @Lor3m in case you want your money back."
    # select a payload just for you to recognize its the donation from your bot
    payload = "Payload"
    provider_token = config('STRIPE_TOKEN')
    start_parameter = "test-payment"
    currency = "EUR"

    price = amount * 100

    context.chat_data['topup_amount'] = price

    prices = [LabeledPrice("Balance Topup", price)]

    context.bot.send_invoice(
        uid, title, description, payload, provider_token, start_parameter, currency, prices
    )

    return ConversationHandler.END


amount_handler = MessageHandler(Filters.text,
                                callback=amount_callback,
                                pass_chat_data=True)


def precheckout_callback(update: Update, context: CallbackContext) -> None:
    query = update.pre_checkout_query

    if query.invoice_payload != 'Payload':

        query.answer(ok=False, error_message="Something went wrong...")

    else:
        query.answer(ok=True)


precheckout_handler = PreCheckoutQueryHandler(callback=precheckout_callback)


def tgpay_success_callback(update: Update, context: CallbackContext) -> None:

    uid = Tools.get_uid(update)

    text = '<b>Thanks for your Payment!</b>\n\nYou will be redirected to the main menu immediately.'

    context.bot.send_message(chat_id=uid,
                             text=text,
                             parse_mode=ParseMode.HTML,
                             reply_markup=ReplyKeyboardRemove())

    amount = context.chat_data['topup_amount']

    user = Tools.get_user(uid)
    Tools.add_balance(user, amount)

    menu_callback(update, context)


tgpay_success_handler = MessageHandler(Filters.successful_payment,
                                       callback=tgpay_success_callback,
                                       pass_chat_data=True)


back_to_balance_menu_handler = MessageHandler(Filters.regex('^{}'.format(back_button)),
                                              callback=balance_callback)


balance_conversation_handler = ConversationHandler(

    entry_points=[balance_handler],

    states={

        VIEWING_BALANCE: [
            back_to_menu_handler,

            top_up_menu_handler


        ],

        CHOOSING_TOPUP_OPTION: [

            telegram_topup_handler,

            back_to_balance_menu_handler

        ],

        ENTERING_AMOUNT: [

            menu_handler,

            amount_handler
        ]

    },

    fallbacks=[menu_handler],
    name='Balance',
    persistent=False
)
