import os
import re
import json

from loguru import logger

from serious_bot import __version__

# templates
from serious_bot.core.botapp import BotApp

# connectors
from serious_bot.connectors.vk_workspace import VKWorkSpaceConnector
from serious_bot.connectors.vk_teams import VKTeamsConnector

# skills
from serious_bot.skills.contains import Contains
from serious_bot.skills.insert import Insert
from serious_bot.skills.white_list import WhiteList

# local imports
from serious_bot.core.conf import Conf
from serious_bot.supply import MatchMock
from serious_bot.supply.helps import (
    HELP_MESSAGE,
    ACCESS_RESTRICTED_HELP_MESSAGE,
    ADMIN_HELP_MESSAGE,
)
from serious_bot.root_markup import (
    ROOT_MARKUP,
    BACK_MARKUP,
)


def _get_product_message(filter_id: str) -> str:
    return (
        "👋 Привет! Я помогу узнать актуальную информацию по серьёзным вопросам.\n\n"
        "Список поддерживаемых вопрсов дополняется.\n"
        "Карточки всех вопрсов можно посмотреть "
        f"по [фильтру](https://example.org) "
        "или на [дашборде](https://example.org).\n\n"
        "Выберите продукт:"
    )


def _is_version_name_product(callback):
    return (
            re.fullmatch(r'^\d+\.\d+_(onpremise|saas)_[a-zA-Z]+$', callback) or MatchMock()
    ).group(0)


def _is_platform_version_name_product(callback):
    return (
            re.fullmatch(r'^(android|ios|desktop|web|backend|deploy)_\d+\.\d+_(onpremise|saas)_[a-zA-Z]+$', callback)
            or MatchMock()
    ).group(0)


class App(BotApp):
    def __init__(self, settings: Conf) -> None:
        super().__init__(
            "serious_bot", __version__, settings.bot_token, settings.bot_api_url)
        self.settings = settings
        self.white_list = WhiteList()

        self.available_products = {
            'vkw': VKWorkSpaceConnector(
                ticket_key=self.settings.vk_workspace_product_card_issue_key,
                jira_url=self.settings.jira_base_url,
                jira_token=self.settings.jira_token,
                gitlab_url=self.settings.gitlab_base_url,
                gitlab_token=self.settings.gitlab_token,
                logger=logger,
            ),
            'vkt': VKTeamsConnector(
                ticket_key=self.settings.vk_teams_product_card_issue_key,
                jira_url=self.settings.jira_base_url,
                jira_token=self.settings.jira_token,
                gitlab_url=self.settings.gitlab_base_url,
                gitlab_token=self.settings.gitlab_token,
                logger=logger,
            ),
        }

        self.bot.send_text(
            chat_id="admin1",
            text=f"✅rebuild <a>@[{self.settings.bot_id}]</a> выполнен",
            parse_mode='HTML'
        )

    def help_command_cb(self, bot, event):
        logger.info('Start help_command_cb')
        logger.info(f'Got event data: {event.data}')

        chat_id_to_reply = event.from_chat
        if chat_id_to_reply in self.white_list.get_white_list():
            self.bot.send_text(
                chat_id=chat_id_to_reply,
                text=HELP_MESSAGE,
                parse_mode='HTML'
            )
            if chat_id_to_reply in self.settings.admins:
                self.bot.send_text(
                    chat_id=chat_id_to_reply,
                    text=ADMIN_HELP_MESSAGE,
                    parse_mode='HTML'
                )
        else:
            self.bot.send_text(
                chat_id=chat_id_to_reply,
                text=ACCESS_RESTRICTED_HELP_MESSAGE,
                parse_mode='HTML'
            )

    def message_cb(self, bot, event):
        logger.debug(f'Got message event: {event}')

        chat_id_to_reply = event.from_chat
        if chat_id_to_reply not in self.white_list.get_white_list():
            self.bot.send_text(
                chat_id=chat_id_to_reply,
                text=ACCESS_RESTRICTED_HELP_MESSAGE,
                parse_mode='HTML'
            )
            return

        if (event.text.lower() not in ["/help", "/add", "/del", "/white_list"]
                and "/insert" not in event.text.lower() and "/contains" not in event.text.lower()):

            self.bot.send_text(
                chat_id=event.from_chat,
                text=_get_product_message(self.settings.vk_tech_products_filter_id),
                parse_mode="MarkdownV2",
                inline_keyboard_markup=f"{json.dumps(ROOT_MARKUP)}"
            )

    def buttons_answer_cb(self, bot, event):
        logger.info('Start buttons_answer_cb')

        callback = event.data['callbackData']
        logger.info(f"Got callback {callback}")

        chat_id_to_reply = event.from_chat
        if chat_id_to_reply not in self.white_list.get_white_list():
            return

        match callback:

            case "vk_workspace":

                product = self.available_products['vkw']
                # product.parse_jira_product_card()
                product.process_product(bot=self.bot, bot_id=self.settings.bot_id, event=event, back_markup=BACK_MARKUP)

            case "vk_teams":

                product = self.available_products['vkt']
                product.parse_jira_product_card()
                product.process_product(bot=self.bot, bot_id=self.settings.bot_id, event=event, back_markup=BACK_MARKUP)

            case "back":

                self.bot.edit_text(
                    chat_id=event.from_chat,
                    msg_id=event.data['message'].get('msgId'),
                    text=_get_product_message(self.settings.vk_tech_products_filter_id),
                    parse_mode="MarkdownV2",
                    inline_keyboard_markup=f"{json.dumps(ROOT_MARKUP)}"
                )

            case "docs":

                self.bot.edit_text(
                    chat_id=event.from_chat,
                    msg_id=event.data['message'].get('msgId'),
                    text="📚Документация по Serious Bot:\n\n"
                         "🔹[Дока](https://example.org)\n\n"
                         "🔶[Репозиторий](https://example.org)",
                    parse_mode="MarkdownV2",
                    inline_keyboard_markup=f"{json.dumps(BACK_MARKUP)}"
                )

            case "feedback":

                self.bot.edit_text(
                    chat_id=event.from_chat,
                    msg_id=event.data['message'].get('msgId'),
                    text="🖋По вопросам и предложениям:\n\n"
                         "→ <a>@[email_сотрудника]</a>",
                    parse_mode="HTML",
                    inline_keyboard_markup=f"{json.dumps(BACK_MARKUP)}"
                )

            case version_name_product if version_name_product := _is_version_name_product(
                    callback
            ):

                # ожидаем формат "23.2_onpremise_vkt"
                parts = version_name_product.split('_')
                version, name, product = (parts[0], parts[1], parts[2])
                logger.info(f'Version _ name _ product: {(version, name, product)}')
                if not version or not name or not product:
                    return

                try:
                    product = self.available_products[product]
                    logger.info(f'Product card: {product.ticket_key}')
                    product.select_platform(bot=self.bot, event=event, version=version, name=name)
                except KeyError:
                    logger.warning(f'Unknown callback: {callback}')

            case platform_version_name_product if platform_version_name_product := _is_platform_version_name_product(
                    callback
            ):

                # ожидаем формат "android_23.2_onpremise_vkt"
                parts = platform_version_name_product.split('_')
                platform, version, name, product = (parts[0], parts[1], parts[2], parts[3])
                logger.info(f'platform _ version _ name _ product: {(platform, version, name, product)}')
                if not platform or not product:
                    return

                try:
                    product = self.available_products[product]
                    logger.info(f'Product card: {product.ticket_key}')
                    product.process_platform(bot=self.bot, event=event, platform=platform, version=version, name=name)
                except KeyError:
                    logger.warning(f'Unknown callback: {callback}')

            case _:
                logger.warning(f'Unknown callback: {callback}')

        self.bot.answer_callback_query(
            query_id=event.data['queryId'],
            text="",
            show_alert=False
        )

    def command_cb(self, bot, event):
        logger.info('Start command_cb')
        logger.info(f'Got event: {event}')

        chat_id_to_reply = event.from_chat
        if chat_id_to_reply not in self.white_list.get_white_list():
            return

        try:
            raw_message = event.text
        except BaseException as exc:
            logger.error(f'Exception occurred while checking text from message from command_cb: {exc}')
            raw_message = ""
        if not raw_message:
            return

        command = raw_message.partition(" ")[0][1:].lower()
        match command:

            case 'contains':

                Contains(raw_message).process(
                    self.available_products,
                    bot,
                    chat_id_to_reply,
                    self.settings.jira_base_url,
                    self.settings.gitlab_base_url
                )

            case 'insert':

                if chat_id_to_reply not in self.settings.admins:
                    self._restricted_access(chat_id_to_reply)
                    return

                Insert(raw_message).process(
                    self.available_products,
                    bot,
                    chat_id_to_reply,
                    self.settings.jira_base_url,
                    self.settings.gitlab_base_url
                )

            case 'add':

                if chat_id_to_reply not in self.settings.admins:
                    self._restricted_access(chat_id_to_reply)
                    return

                self.white_list.add(raw_message, bot, self.settings.bot_id, chat_id_to_reply)

            case 'del':

                if chat_id_to_reply not in self.settings.admins:
                    self._restricted_access(chat_id_to_reply)
                    return

                self.white_list.delete(raw_message, bot, self.settings.bot_id, chat_id_to_reply)

            case 'white_list':

                self.white_list.get(bot, self.settings.bot_id, chat_id_to_reply)

            case 'help':
                pass

            case _:
                logger.warning(f'Unknown command: {command}')

    def _restricted_access(self, chat_id_to_reply: str):
        self.bot.senxxd_text(
            chat_id=chat_id_to_reply,
            text="Не удалось❗\n"
                 "Это действие не разрешено в вашей роли",
            parse_mode='HTML'
        )


def main() -> None:
    settings = Conf.from_yaml(os.getenv('CONFIG_TEMPLATE'))

    app = App(settings=settings)
    app.main()


if __name__ == "__main__":
    main()
