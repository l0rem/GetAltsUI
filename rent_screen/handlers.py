from telegram import Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, MessageHandler, ConversationHandler, Filters, CallbackQueryHandler
from tools import Tools, countries_dict, reverse_countries_dict, emojified_countries_list
from keyboards import menu_keyboard, back_to_menu_kb, rent_number_button, pagination_kb, \
    change_service_bttn, phone_buttons
from .texts import rent_header, rent_form, service_unsupported_text, low_balance_text, phone_form,\
    phone_stripped_form
from main_screen.handlers import menu_handler, back_to_menu_handler
from wrapper.api_core import backend
from wrapper.datatype import SmsTypes
from datetime import datetime, timedelta


VIEWING_RENT_MENU = range(1)


def rent_menu_callback(update: Update, context: CallbackContext):

    uid = Tools.get_uid(update)

    context.chat_data['uid'] = uid

    user = Tools.get_user(uid)

    context.chat_data['user'] = user

    default_country = Tools.get_default_country(user)

    default_service = 'Telegram'

    context.chat_data['current_service'] = default_service

    free_numbers = Tools.services_merger(backend.get_prices_by_country(country=default_country))

    country_name = Tools.get_country_name(default_country)

    emoji = emojified_countries_list.get(country_name).get('emoji')

    context.chat_data['free_numbers'] = free_numbers

    context.chat_data['current_country'] = default_country

    rent_number_bttn = InlineKeyboardButton(text=rent_number_button,
                                            callback_data=f'rent_number:{default_service}:{default_country}')

    change_country_bttn = InlineKeyboardButton(text=f'{emoji} {country_name}',
                                               callback_data='change_country')

    rent_keyboard = InlineKeyboardMarkup([[rent_number_bttn, change_country_bttn],
                                          [change_service_bttn]])

    mid0 = context.bot.send_message(chat_id=uid,
                                    text=rent_header,
                                    parse_mode=ParseMode.HTML,
                                    reply_markup=back_to_menu_kb).message_id

    mid1 = context.bot.send_message(chat_id=uid,
                                    text=rent_form.format(default_service,
                                                          free_numbers.get(default_service).get('cost') / 100,
                                                          free_numbers.get(default_service).get('amount')),
                                    parse_mode=ParseMode.HTML,
                                    reply_markup=rent_keyboard).message_id

    context.chat_data['messages_to_delete'] = [mid0, mid1]

    return VIEWING_RENT_MENU


rent_menu_handler = MessageHandler(Filters.regex('^{}'.format(menu_keyboard[0][0])),
                                   callback=rent_menu_callback,
                                   pass_chat_data=True)


def change_country_callback(update: Update, context: CallbackContext):

    uid = context.chat_data['uid']

    countries = sorted(list(countries_dict.values()), key=str.lower)

    context.chat_data['countries_list'] = countries

    keyboard = list()

    for i in range(0, 3 * 5, 3):
        sublist = list()
        for k in range(3):
            country_name = countries[i + k]
            try:
                emoji = emojified_countries_list.get(country_name).get('emoji')
            except AttributeError:
                emoji = ''
            button = InlineKeyboardButton(text=f'{emoji} {country_name}',
                                          callback_data=f'select_country:{countries[i + k]}')
            sublist.append(button)
        keyboard.append(sublist)

    next_inline_button = InlineKeyboardButton(text=pagination_kb[1],
                                              callback_data='country_page:1')

    keyboard.append([next_inline_button])

    context.bot.edit_message_reply_markup(chat_id=uid,
                                          message_id=update.effective_message.message_id,
                                          reply_markup=InlineKeyboardMarkup(keyboard))

    return VIEWING_RENT_MENU


change_country_handler = CallbackQueryHandler(callback=change_country_callback,
                                              pattern='change_country',
                                              pass_chat_data=True)


def switch_country_page_callback(update: Update, context: CallbackContext):

    uid = context.chat_data['uid']

    callback_data = update.callback_query.data
    page = int(callback_data.split(':')[1])

    countries = context.chat_data['countries_list']

    keyboard = list()

    previous_inline_button = InlineKeyboardButton(text=pagination_kb[0],
                                                  callback_data=f'country_page:{page - 1}')

    next_inline_button = InlineKeyboardButton(text=pagination_kb[1],
                                              callback_data=f'country_page:{page + 1}')

    upper_range = (page * 15) + 3 * 5
    lower_range = (page * 15) - 3 * 5
    if upper_range >= len(countries):
        upper_range = len(countries) - 1
        lower_row = [previous_inline_button]

    elif lower_range < 0:
        lower_row = [next_inline_button]

    else:
        lower_row = [previous_inline_button, next_inline_button]

    for i in range(page * 15, upper_range, 3):
        sublist = list()
        for k in range(3):
            country_name = countries[i + k]
            try:
                emoji = emojified_countries_list.get(country_name).get('emoji')
            except AttributeError:
                emoji = ''
            button = InlineKeyboardButton(text=f'{emoji} {country_name}',
                                          callback_data=f'select_country:{countries[i + k]}')
            sublist.append(button)
        keyboard.append(sublist)

    keyboard.append(lower_row)

    context.bot.edit_message_reply_markup(chat_id=uid,
                                          message_id=update.effective_message.message_id,
                                          reply_markup=InlineKeyboardMarkup(keyboard))

    return VIEWING_RENT_MENU


switch_country_page_handler = CallbackQueryHandler(callback=switch_country_page_callback,
                                                   pattern='country_page:(.*)',
                                                   pass_chat_data=True)


def select_country_callback(update: Update, context: CallbackContext):

    uid = context.chat_data['uid']

    selected_country = update.callback_query.data.split(':')[1]

    country_id = reverse_countries_dict.get(selected_country)

    try:
        emoji = emojified_countries_list.get(selected_country).get('emoji')
    except AttributeError:
        emoji = ''

    current_service = context.chat_data['current_service']

    free_numbers = Tools.services_merger(backend.get_prices_by_country(country=country_id))

    context.chat_data['free_numbers'] = free_numbers

    context.chat_data['current_country'] = country_id

    rent_number_bttn = InlineKeyboardButton(text=rent_number_button,
                                            callback_data=f'rent_number:{current_service}:{country_id}')

    change_country_bttn = InlineKeyboardButton(text=f'{emoji} {selected_country}',
                                               callback_data='change_country')

    rent_keyboard = InlineKeyboardMarkup([[rent_number_bttn, change_country_bttn],
                                          [change_service_bttn]])

    service_data = free_numbers.get(current_service)

    if service_data is None:
        context.bot.answer_callback_query(
            callback_query_id=update.callback_query.id,
            text=service_unsupported_text
        )

        return VIEWING_RENT_MENU

    cost = service_data.get('cost') / 100
    amount = service_data.get('amount')

    context.bot.edit_message_text(chat_id=uid,
                                  message_id=update.effective_message.message_id,
                                  text=rent_form.format(current_service,
                                                        cost,
                                                        amount),
                                  parse_mode=ParseMode.HTML,
                                  reply_markup=rent_keyboard)

    return VIEWING_RENT_MENU


select_country_handler = CallbackQueryHandler(callback=select_country_callback,
                                              pattern='select_country:(.*)',
                                              pass_chat_data=True)


def change_service_callback(update: Update, context: CallbackContext):

    uid = context.chat_data['uid']

    free_numbers = context.chat_data['free_numbers']

    services = sorted(list(free_numbers.keys()), key=str.lower)

    context.chat_data['services_list'] = services

    keyboard = list()

    for i in range(0, 3 * 5, 3):
        sublist = list()
        for k in range(3):
            button = InlineKeyboardButton(text=services[i + k],
                                          callback_data='select_service:{}'.format(services[i + k]))
            sublist.append(button)
        keyboard.append(sublist)

    next_inline_button = InlineKeyboardButton(text=pagination_kb[1],
                                              callback_data='service_page:1')

    keyboard.append([next_inline_button])

    context.bot.edit_message_reply_markup(chat_id=uid,
                                          message_id=update.effective_message.message_id,
                                          reply_markup=InlineKeyboardMarkup(keyboard))

    return VIEWING_RENT_MENU


change_service_handler = CallbackQueryHandler(callback=change_service_callback,
                                              pattern='change_service',
                                              pass_chat_data=True)


def switch_service_page_callback(update: Update, context: CallbackContext):

    uid = context.chat_data['uid']

    callback_data = update.callback_query.data
    page = int(callback_data.split(':')[1])

    services = context.chat_data['services_list']

    keyboard = list()

    previous_inline_button = InlineKeyboardButton(text=pagination_kb[0],
                                                  callback_data='service_page:{}'.format(page - 1))

    next_inline_button = InlineKeyboardButton(text=pagination_kb[1],
                                              callback_data='service_page:{}'.format(page + 1))

    upper_range = (page * 15) + 3 * 5
    lower_range = (page * 15) - 3 * 5
    if upper_range >= len(services):
        upper_range = len(services) - 1
        lower_row = [previous_inline_button]

    elif lower_range < 0:
        lower_row = [next_inline_button]

    else:
        lower_row = [previous_inline_button, next_inline_button]
    for i in range(page * 15, upper_range, 3):
        sublist = list()
        for k in range(3):
            button = InlineKeyboardButton(text=services[i + k],
                                          callback_data='select_service:{}'.format(services[i + k]))
            sublist.append(button)
        keyboard.append(sublist)

    keyboard.append(lower_row)

    context.bot.edit_message_reply_markup(chat_id=uid,
                                          message_id=update.effective_message.message_id,
                                          reply_markup=InlineKeyboardMarkup(keyboard))

    return VIEWING_RENT_MENU


switch_service_page_handler = CallbackQueryHandler(callback=switch_service_page_callback,
                                                   pattern='service_page:(.*)',
                                                   pass_chat_data=True)


def select_service_callback(update: Update, context: CallbackContext):

    uid = context.chat_data['uid']

    selected_service = update.callback_query.data.split(':')[1]

    context.chat_data['current_service'] = selected_service

    free_numbers = context.chat_data['free_numbers']

    current_country_id = context.chat_data['current_country']

    country_name = countries_dict.get(current_country_id)

    emoji = emojified_countries_list.get(country_name).get('emoji')

    rent_number_bttn = InlineKeyboardButton(text=rent_number_button,
                                            callback_data='rent_number:{}:{}'.format(selected_service,
                                                                                     current_country_id))

    change_country_bttn = InlineKeyboardButton(text=f'{emoji} {country_name}',
                                               callback_data='change_country')

    rent_keyboard = InlineKeyboardMarkup([[rent_number_bttn, change_country_bttn],
                                          [change_service_bttn]])

    context.bot.edit_message_text(chat_id=uid,
                                  message_id=update.effective_message.message_id,
                                  text=rent_form.format(selected_service,
                                                        free_numbers.get(selected_service).get('cost') / 100,
                                                        free_numbers.get(selected_service).get('amount')),
                                  parse_mode=ParseMode.HTML,
                                  reply_markup=rent_keyboard)

    return VIEWING_RENT_MENU


select_service_handler = CallbackQueryHandler(callback=select_service_callback,
                                              pattern='select_service:(.*)',
                                              pass_chat_data=True)


def rent_number_callback(update: Update, context: CallbackContext):

    user = context.chat_data['user']

    balance = user.balance.get()
    free_numbers = context.chat_data['free_numbers']
    current_service = context.chat_data['current_service']
    current_country = context.chat_data['current_country']
    current_country_name = Tools.convert_country_id_to_name(current_country)

    price = free_numbers.get(current_service).get('cost')

    if balance.amount < price:

        context.bot.answer_callback_query(
            callback_query_id=update.callback_query.id,
            text=low_balance_text)

        return VIEWING_RENT_MENU

    Tools.deduct_balance(user, price)

    time = datetime.now() + timedelta(minutes=19)
    try:
        rent = backend.rent_number(service=Tools.convert_service_name_to_id(current_service),
                                   country=current_country)
    except Exception as e:
        print(e)
        context.bot.answer_callback_query(update.callback_query.id,
                                          text='Sorry, but there are no numbers left. Come back later!')
        return VIEWING_RENT_MENU

    data = {rent.id: {'rent': rent,
                      'price': price,
                      'time': time}}

    rents = context.chat_data.get('current_rents')
    if rents is None:
        context.chat_data['current_rents'] = data
    else:
        context.chat_data['current_rents'].update(data)

    sms_sent_button = InlineKeyboardButton(text=phone_buttons[0],
                                           callback_data=f'sms_sent:{rent.id}')

    cancel_rent_button = InlineKeyboardButton(text=phone_buttons[1],
                                              callback_data=f'cancel_rent:{rent.id}')

    initial_phone_keyboard = InlineKeyboardMarkup([[sms_sent_button],
                                                  [cancel_rent_button]])

    context.bot.edit_message_text(chat_id=user.uid,
                                  message_id=update.effective_message.message_id,
                                  parse_mode=ParseMode.HTML,
                                  text=phone_form.format(current_service,
                                                         current_country_name,
                                                         rent.phone_number,
                                                         'Not sent.'),
                                  reply_markup=initial_phone_keyboard)

    return VIEWING_RENT_MENU


rent_number_handler = CallbackQueryHandler(callback=rent_number_callback,
                                           pattern='rent_number:(.*)',
                                           pass_chat_data=True)


def cancel_rent_callback(update: Update, context: CallbackContext):
    user = context.chat_data['user']
    rent_id = update.callback_query.data.split(':')[1]

    rent_data = context.chat_data['current_rents'].get(rent_id)
    rent = rent_data.get('rent')
    price = rent_data.get('price')

    if rent_data.get('codes') is None:
        Tools.add_balance(user, price)
        rent.cancel()
    else:
        rent.cancel()
    for mid in context.chat_data['messages_to_delete']:
        context.bot.delete_message(chat_id=user.uid,
                                   message_id=mid)

    rent_menu_callback(update, context)

    return VIEWING_RENT_MENU


cancel_rent_handler = CallbackQueryHandler(callback=cancel_rent_callback,
                                           pattern='cancel_rent:(.*)',
                                           pass_chat_data=True)


def sms_code_check_callback(context: CallbackContext):
    chat_data = context.job.context[1]
    rent_id = context.job.context[0]
    current_service = chat_data['current_service']
    rent_data = chat_data['current_rents'].get(rent_id)

    if rent_data is None:
        context.job.schedule_removal()

        return

    rent = rent_data.get('rent')
    user = chat_data['user']

    if datetime.now() > rent_data.get('time'):
        rent.cancel()

        for mid in chat_data['messages_to_delete']:
            context.bot.delete_message(chat_id=user.uid,
                                       message_id=mid)

        context.job.schedule_removal()

        return

    try:
        status = backend.get_number_status(rent_id)

    except Exception as e:
        print(e)

        for mid in chat_data['messages_to_delete']:
            context.bot.delete_message(chat_id=user.uid,
                                       message_id=mid)

        context.job.schedule_removal()
        return

    code = status.get('code')
    if code is not None:

        if rent_data.get('codes') is None:
            rent_data.update({'codes': [code]})
        elif code in rent_data.get('codes'):
            return
        else:
            rent_data.update({'codes': rent_data.get('codes').append(code)})

        chat_data['current_rents'].update({rent_id: rent_data})

        current_country_name = Tools.convert_country_id_to_name(chat_data['current_country'])

        rent_done_button = InlineKeyboardButton(text=phone_buttons[2],
                                                callback_data=f'rent_done:{rent_id}')

        one_more_code_button = InlineKeyboardButton(text=phone_buttons[3],
                                                    callback_data=f'one_more_code:{rent_id}')

        sms_received_keyboard = InlineKeyboardMarkup([[rent_done_button],
                                                      [one_more_code_button]])

        context.bot.edit_message_text(chat_id=user.uid,
                                      message_id=chat_data['messages_to_delete'][1],
                                      text=phone_stripped_form.format(current_service,
                                                                      current_country_name,
                                                                      rent.phone_number,
                                                                      code),
                                      parse_mode=ParseMode.HTML,
                                      reply_markup=sms_received_keyboard)

        context.job.schedule_removal()

        return VIEWING_RENT_MENU


def sms_sent_callback(update: Update, context: CallbackContext):
    user = context.chat_data['user']
    rent_id = update.callback_query.data.split(':')[1]

    rent_data = context.chat_data['current_rents'].get(rent_id)
    current_service = context.chat_data['current_service']
    current_country_name = Tools.convert_country_id_to_name(context.chat_data['current_country'])
    rent = rent_data.get('rent')

    rent.was_sent()

    cancel_rent_button = InlineKeyboardButton(text=phone_buttons[1],
                                              callback_data=f'cancel_rent:{rent.id}')

    sms_sent_keyboard = InlineKeyboardMarkup([[cancel_rent_button]])

    context.bot.edit_message_text(chat_id=user.uid,
                                  message_id=update.effective_message.message_id,
                                  text=phone_form.format(current_service,
                                                         current_country_name,
                                                         rent.phone_number,
                                                         'Waiting...'),
                                  parse_mode=ParseMode.HTML,
                                  reply_markup=sms_sent_keyboard)

    context.job_queue.run_repeating(callback=sms_code_check_callback, interval=5, first=0,
                                    context=[rent_id, context.chat_data])

    return VIEWING_RENT_MENU


sms_sent_handler = CallbackQueryHandler(callback=sms_sent_callback,
                                        pattern='sms_sent:(.*)',
                                        pass_chat_data=True,
                                        pass_job_queue=True)


def rent_done_callback(update: Update, context: CallbackContext):
    user = context.chat_data['user']
    rent_id = update.callback_query.data.split(':')[1]

    backend.set_number_status(rent_id, SmsTypes.Status.End)

    context.chat_data['current_rents'].pop(rent_id)

    for mid in context.chat_data['messages_to_delete']:
        context.bot.delete_message(chat_id=user.uid,
                                   message_id=mid)

    rent_menu_callback(update, context)

    return VIEWING_RENT_MENU


rent_done_handler = CallbackQueryHandler(callback=rent_done_callback,
                                         pattern='rent_done:(.*)',
                                         pass_chat_data=True)


def one_more_sms_callback(update: Update, context: CallbackContext):
    user = context.chat_data['user']
    rent_id = update.callback_query.data.split(':')[1]
    rent_data = context.chat_data['current_rents'].get(rent_id)
    rent = rent_data.get('rent')
    current_service = context.chat_data['current_service']
    current_country_name = Tools.convert_country_id_to_name(context.chat_data['current_country'])
    try:
        backend.set_number_status(rent_id, SmsTypes.Status.OneMoreCode)
    except Exception as e:
        print(e)
        context.bot.answer_callback_query(callback_query_id=update.callback_query.id,
                                          text='Sorry, but you probably tried to fool the bot. Text @Lor3m.')

        context.chat_data['current_rents'].pop(rent_id)

        for mid in context.chat_data['messages_to_delete']:
            context.bot.delete_message(chat_id=user.uid,
                                       message_id=mid)

        rent_menu_callback(update, context)

        return VIEWING_RENT_MENU

    cancel_rent_button = InlineKeyboardButton(text=phone_buttons[1],
                                              callback_data=f'cancel_rent:{rent.id}')

    sms_sent_keyboard = InlineKeyboardMarkup([[cancel_rent_button]])

    context.bot.edit_message_text(chat_id=user.uid,
                                  message_id=update.effective_message.message_id,
                                  text=phone_stripped_form.format(current_service,
                                                                  current_country_name,
                                                                  rent.phone_number,
                                                                  'Waiting...'),
                                  parse_mode=ParseMode.HTML,
                                  reply_markup=sms_sent_keyboard)

    context.job_queue.run_repeating(callback=sms_code_check_callback, interval=5, first=0,
                                    context=[rent_id, context.chat_data])

    return VIEWING_RENT_MENU


one_more_sms_handler = CallbackQueryHandler(callback=one_more_sms_callback,
                                            pattern='one_more_code:(.*)',
                                            pass_chat_data=True)

rent_conversation_handler = ConversationHandler(

    entry_points=[rent_menu_handler],

    states={

        VIEWING_RENT_MENU: [
            back_to_menu_handler,

            change_country_handler,

            switch_country_page_handler,

            select_country_handler,

            change_service_handler,

            switch_service_page_handler,

            select_service_handler,

            rent_number_handler,

            cancel_rent_handler,

            sms_sent_handler,

            rent_done_handler,

            one_more_sms_handler
        ]

    },

    fallbacks=[menu_handler],
    name='Rent',
    persistent=True
)
