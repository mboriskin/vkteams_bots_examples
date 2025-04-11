import re
import asyncio

from serious_bot.connectors.vk_teams.platforms.android import Android
from serious_bot.connectors.vk_teams.platforms.ios import IOS


ALLOWED_PATTERN = r"^/insert ((ANDROID|IOS)-\d+) (\S+)$"


class Insert():
    def __init__(self, raw_message) -> None:
        self.match = re.match(ALLOWED_PATTERN, raw_message)
        if self.match:
            self.task_key = self.match.group(1)
            self.release_branch = self.match.group(3)

    def process(self, available_products, bot, chat_id_to_reply, jira_base_url, gitlab_base_url):

        if not self.match:
            bot.send_text(
                chat_id=chat_id_to_reply,
                text="Неправильно указан таск и/или релиз ветка.\nНужно так:\n\n"
                     "<pre>/insert MYPROJECT-3434 release_branch-25.5.5</pre>",
                parse_mode='HTML'
            )
            return

        if "IMA" in self.task_key:

            bot.send_text(
                chat_id=chat_id_to_reply,
                text=f"Таск VK Teams Android: [{self.task_key}]"
                     f"({jira_base_url}/browse/{self.task_key})\n"
                     f"в релиз ветку [{self.release_branch}]"
                     f"(https://example.org)\n\n"
                     "в процессе... Ожидайте ⏳",
                parse_mode='MarkdownV2'
            )

            asyncio.run(
                Android(product=available_products["vkt"]).process_jira_task_to_release(
                    jira_task_key=self.task_key,
                    release_branch=self.release_branch,
                    bot=bot,
                    chat_id_to_reply=chat_id_to_reply,
                    gitlab_url=gitlab_base_url,
                    jira_url=jira_base_url,
                )
            )

        elif "IMIOS" in self.task_key:

            bot.send_text(
                chat_id=chat_id_to_reply,
                text=f"Таск VK Teams iOS: [{self.task_key}]"
                     f"({jira_base_url}/browse/{self.task_key})\n"
                     f"в релиз ветку [{self.release_branch}]"
                     f"(https://example.org)\n\n"
                     "в процессе... Ожидайте ⏳",
                parse_mode='MarkdownV2'
            )

            asyncio.run(
                IOS(product=available_products["vkt"]).process_jira_task_to_release(
                    jira_task_key=self.task_key,
                    release_branch=self.release_branch,
                    bot=bot,
                    chat_id_to_reply=chat_id_to_reply,
                    gitlab_url=gitlab_base_url,
                    jira_url=jira_base_url,
                )
            )

        else:
            bot.send_text(
                chat_id=chat_id_to_reply,
                text="К сожалению, этот Jira проект в данный момент не поддерживается системой.\n"
                     "Поддерживаемые проекты:\n\n"
                     "IMA, IMIOS",
                parse_mode='MarkdownV2'
            )
