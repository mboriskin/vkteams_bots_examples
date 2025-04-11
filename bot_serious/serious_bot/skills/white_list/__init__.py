import re

from serious_bot.database.sql_worker import (
    load_from_db,
    save_to_db,
    delete_from_db
)


TABLE_NANE = "white_list"


class WhiteList:
    def __init__(self) -> None:
        self._white_list = load_from_db(table_name=TABLE_NANE)

    def get_white_list(self) -> []:
        return self._white_list

    def get(self, bot, bot_id, chat_id_to_reply):
        mentions = ''
        for user_id in self._white_list:
            mentions += f"<a>@[{user_id}]</a>\n"
        bot.send_text(
            chat_id=chat_id_to_reply,
            text="Следующие пользователи могут взаимодействовать с "
                 f"<a>@[{bot_id}]</a>:\n"
                 f"{mentions}",
            parse_mode='HTML'
        )

    def add(self, raw_message, bot, bot_id, chat_id_to_reply):
        white_list = self._white_list
        whom = ' '.join(raw_message.split(' ')[1:])
        corp_emails = re.findall(r'\[(.*?)\]', whom)

        if save_to_db(table_name=TABLE_NANE, new_users=corp_emails):

            mentions = ''
            for email in corp_emails:
                mentions += f"<a>@[{email}]</a>\n"
                white_list.append(email)

            bot.send_text(
                chat_id=chat_id_to_reply,
                text="Успех!🎉\n"
                     "Следующие пользователи теперь могут взаимодействовать с "
                     f"<a>@[{bot_id}]</a>:\n"
                     f"{mentions}",
                parse_mode='HTML'
            )

            self._white_list = white_list
            return

        bot.send_text(
            chat_id=chat_id_to_reply,
            text="Не удалось❗\n"
                 "Пожалуйста, попробуйте позже",
            parse_mode='HTML'
        )

    def delete(self, raw_message, bot, bot_id, chat_id_to_reply):
        white_list = self._white_list
        whom = ' '.join(raw_message.split(' ')[1:])
        corp_emails = re.findall(r'\[(.*?)\]', whom)

        if delete_from_db(table_name=TABLE_NANE, drop_users=corp_emails):
            mentions = ''
            for email in corp_emails:
                mentions += f"<a>@[{email}]</a>\n"
                white_list.remove(email) if email in white_list else None

            bot.send_text(
                chat_id=chat_id_to_reply,
                text="Успех!🎉\n"
                     "Следующие пользователи больше не смогут взаимодействовать с "
                     f"<a>@[{bot_id}]</a>:\n"
                     f"{mentions}",
                parse_mode='HTML'
            )
            return

        bot.send_text(
            chat_id=chat_id_to_reply,
            text="Не удалось❗\n"
                 "Пожалуйста, попробуйте позже",
            parse_mode='HTML'
        )
