import json

from serious_bot.connectors.vk_teams.platforms import VKTeamsPlatform


class Web(VKTeamsPlatform):
    def __init__(self, product):
        super().__init__(product)

    def process(self, bot, event, back_markup, version, product_raw):
        bot.edit_text(
            chat_id=event.from_chat,
            msg_id=event.data['message'].get('msgId'),
            text="Поддержка данной платформы в процессе реализации",
            parse_mode="MarkdownV2",
            inline_keyboard_markup=f"{json.dumps(back_markup)}"
        )
