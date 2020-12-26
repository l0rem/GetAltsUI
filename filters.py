from telegram.ext import MessageFilter
from wrapper.dbmodels import User, db


class NewUserFilter(MessageFilter):
    def filter(self, message):
        with db:
            user = User.select().where(User.uid == message.from_user.id)
            if user.exists():
                return False
            elif not user.exists():
                return True


new_user_filter = NewUserFilter()