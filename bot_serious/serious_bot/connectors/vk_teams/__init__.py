import re
import json

from serious_bot.connectors.vk_teams.platforms.android import Android
from serious_bot.connectors.vk_teams.platforms.backend import Backend
from serious_bot.connectors.vk_teams.platforms.deploy import Deploy
from serious_bot.connectors.vk_teams.platforms.desktop import Desktop
from serious_bot.connectors.vk_teams.platforms.ios import IOS
from serious_bot.connectors.vk_teams.platforms.web import Web
from serious_bot.core.product import Product


def _platform_not_implemented_yet(bot, event, back_platform_markup):
    bot.edit_text(
        chat_id=event.from_chat,
        msg_id=event.data['message'].get('msgId'),
        text="Поддержка данной платформы в процессе реализации",
        parse_mode="MarkdownV2",
        inline_keyboard_markup=f"{json.dumps(back_platform_markup)}"
    )


class VKTeamsConnector(Product):
    """Root object for VK Teams Product"""

    def __init__(self, ticket_key, jira_url, jira_token, gitlab_url, gitlab_token, logger):
        super().__init__(ticket_key, jira_url, jira_token, gitlab_url, gitlab_token)
        self.logger = logger

        self.allowed_platforms = [
            "android",
            "ios",
            "desktop",
            "web",
            "backend",
            "deploy",
        ]

    def process_product(self, bot, bot_id, event, back_markup):
        """Описание

        Args:
            bot: описание
            event: описание
            bot_id: описание
            back_markup: описание

        Returns:
            описание

        """

        if not self.releases_in_process_now:
            bot.edit_text(
                chat_id=event.from_chat,
                msg_id=event.data['message'].get('msgId'),
                text="Релизов <a href='https://example.org'>VK Teams</a> "
                     "в <strong>ACTIVE</strong> или <strong>PLANNING</strong> не найдено.",
                parse_mode='HTML',
                inline_keyboard_markup=f"{json.dumps(back_markup)}",
            )
            return

        releases_in_process_markup = []
        for release in self.releases_in_process_now:
            version_match = re.search(r'\d+\.\d+', release)
            version = version_match.group(0) if version_match else ''
            if 'On-premise' in release:
                type_ = 'onpremise'
            elif 'SaaS' in release:
                type_ = 'saas'
            else:
                type_ = ''
            if version and type_:
                releases_in_process_markup.append(
                    [
                        {
                            "text": release, "callbackData": f"{version}_{type_}_vkt"
                        }
                    ]
                )
            else:
                releases_in_process_markup.append(
                    [
                        {
                            "text": release, "callbackData": "unknown_release"
                        }
                    ]
                )

        releases_in_process_markup.append(
            [
                {
                    "text": "Назад", "callbackData": "back"
                }
            ]
        )

        bot.edit_text(
            chat_id=event.from_chat,
            msg_id=event.data['message'].get('msgId'),
            text="Релизы <a href='https://example.org'>VK Teams</a> "
                 "в статусах <strong>ACTIVE</strong> и <strong>PLANNING</strong>.\n\n"
                 "Выберите релиз, о котором хотите узнать больше:",
            parse_mode="HTML",
            inline_keyboard_markup=f"{json.dumps(releases_in_process_markup)}"
        )

    def select_platform(self, bot, event, version, name):
        """Описание

        Args:
            bot: описание
            event: описание
            version: описание
            name: описание

        Returns:
            описание

        """
        platforms_markup = []
        for platform in self.allowed_platforms:
            platforms_markup.append([
                {
                    "text": platform, "callbackData": f"{platform}_{version}_{name}_vkt"
                }
            ])

        platforms_markup.append(
            [
                {
                    "text": "Назад", "callbackData": "vk_teams"
                }
            ],
        )

        bot.edit_text(
            chat_id=event.from_chat,
            msg_id=event.data['message'].get('msgId'),
            text=f"VKT {version} - {name}\n\n"
                 f"Информация по какой платформе вас интересует?",
            parse_mode="MarkdownV2",
            inline_keyboard_markup=f"{json.dumps(platforms_markup)}"
        )

    def process_platform(self, bot, event, platform, version, name):
        """Описание

        Args:
            bot: описание
            event: описание
            platform: описание
            version: описание
            name: описание

        Returns:
            описание

        """
        back_platform_markup = [
            [
                {
                    "text": "Назад", "callbackData": f"{version}_{name}_vkt"
                }
            ],
        ]

        if platform not in self.allowed_platforms:
            _platform_not_implemented_yet(bot, event, back_platform_markup)
            return

        match platform:

            case "android":

                Android(self).process(bot, event, back_platform_markup, version, name)

            case "ios":

                IOS(self).process(bot, event, back_platform_markup, version, name)

            case "desktop":

                Desktop(self).process(bot, event, back_platform_markup, version, name)

            case "web":

                Web(self).process(bot, event, back_platform_markup, version, name)

            case "backend":

                Backend(self).process(bot, event, back_platform_markup, version, name)

            case "deploy":

                Deploy(self).process(bot, event, back_platform_markup, version, name)
