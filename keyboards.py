from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup


menu_keyboard = [['\U0001F6D2 Services', '\U0001F4B0 Balance'],
                 ['\U00002699 Settings', '\U0001F310 API'],
                 ['\U00002139 Help']]

menu_kb = ReplyKeyboardMarkup(keyboard=menu_keyboard,
                              resize_keyboard=True,
                              one_time_keyboard=True)

back_button = '\U00002B05 Back'

back_kb = ReplyKeyboardMarkup(keyboard=[[back_button]],
                              resize_keyboard=True,
                              one_time_keyboard=True)

back_to_menu_button = '\U00002B05 Back to Menu'

back_to_menu_kb = ReplyKeyboardMarkup(keyboard=[[back_to_menu_button]],
                                      resize_keyboard=True,
                                      one_time_keyboard=True)

pagination_kb = ['\U00002B05 Previous', 'Next \U000027A1']


change_service_button = '\U00002935 Change service'

rent_number_button = '\U0001F4F2 Rent'

change_service_bttn = InlineKeyboardButton(text=change_service_button,
                                           callback_data='change_service')

phone_buttons = ['\U0001F4E8 SMS sent', '\U0000274C Cancel', '\U00002714 Done', '\U0001F501 One more SMS']

topup_button = 'Top Up'

topup_options = ['TelegramPay']

