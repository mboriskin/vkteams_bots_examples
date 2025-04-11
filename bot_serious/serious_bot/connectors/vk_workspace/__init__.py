import json

from serious_bot.core.product import Product


class VKWorkSpaceConnector(Product):
    def __init__(self, ticket_key, jira_url, jira_token, gitlab_url, gitlab_token, logger):
        super().__init__(ticket_key, jira_url, jira_token, gitlab_url, gitlab_token)
        self.logger = logger

    def process_product(self, bot, bot_id, event, back_markup):
        bot.edit_text(
            chat_id=event.from_chat,
            msg_id=event.data['message'].get('msgId'),
            text="Поддержка продукта VK Workspace "
                 "(<a href='https://example.org'>Продукт</a>) "
                 f"пока не реализована в <a>@[{bot_id}]</a>\n\n"
                 f"Для уточнения информации, пожалуйста, напишите <a>@[email_коллеги]</a>",
            parse_mode='HTML',
            inline_keyboard_markup=f"{json.dumps(back_markup)}",
        )

    def select_platform(self, bot, event, version, name):
        pass

    def process_platform(self, bot, event, platform, version, name):
        pass
