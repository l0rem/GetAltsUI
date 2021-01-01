from telegram import Update
from wrapper.dbmodels import db, User, Balance, Token, DefaultCountry
import secrets
from datetime import datetime
from wrapper.api_parser import countries_dict, services_dict, reverse_services_dict, reverse_countries_dict,\
    emojified_countries_list
from forex_python.converter import CurrencyRates


class Tools:

    @staticmethod
    def get_uid(update: Update):

        if update.callback_query is not None:
            return update.callback_query.from_user.id

        return update.effective_message.from_user.id

    @staticmethod
    def create_user(username: str, uid: int):
        with db:
            user = User.create(uid=uid,
                               username=username,
                               joined_on=datetime.now())

            Balance.create(user=user)

            Token.create(user=user,
                         hash=secrets.token_hex(16))

            DefaultCountry.create(user=user)

            return user

    @staticmethod
    def get_user(uid: int):
        with db:
            user = User.get(User.uid == uid)

            return user

    @staticmethod
    def get_balance(user: User):
        with db:
            return user.balance.get().amount / 100

    @staticmethod
    def set_balance(user: User, value: int):
        with db:
            balance = user.balance.get()

            balance.amount = value

            balance.save()

            return balance

    @staticmethod
    def add_balance(user: User, value: int):
        with db:
            balance = user.balance.get()

            balance.amount += value

            balance.save()

            return balance

    @staticmethod
    def deduct_balance(user: User, value: int):
        with db:
            balance = user.balance.get()

            balance.amount -= value

            balance.save()

            return balance

    @staticmethod
    def get_default_country(user: User):
        with db:

            default_county = user.default_country.get().country

            return default_county

    @staticmethod
    def get_country_name(country_id):
        return countries_dict.get(str(country_id))

    @staticmethod
    def services_merger(free_numbers):
        response = dict()
        data = list(free_numbers.values())[0]

        rates = CurrencyRates()
        rate = rates.get_rate('RUB', 'EUR')

        for service in data:
            if service[-2:] == '_1':
                pass
            else:
                full_name = reverse_services_dict.get(service + '_0')
                cost = data.get(service).get('cost')
                cost = int(100 * (round(cost * rate, 2))) + 5
                amount = data.get(service).get('count')

                response.update({full_name: {'short_name': service,
                                             'cost': cost,
                                             'amount': amount}})

        return response

    @staticmethod
    def convert_service_name_to_id(service_name):
        return services_dict.get(service_name)

    @staticmethod
    def convert_service_id_to_name(service_id):
        return reverse_services_dict.get(service_id)

    @staticmethod
    def convert_country_name_to_id(country_name):
        return reverse_countries_dict.get(country_name)

    @staticmethod
    def convert_country_id_to_name(country_id):
        return countries_dict.get(country_id)
