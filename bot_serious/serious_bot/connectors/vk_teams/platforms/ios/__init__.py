import json

from serious_bot.supply import retry_in_rc

from serious_bot.connectors.vk_teams.platforms import VKTeamsPlatform


VK_TEAMS_IOS_PROJECT_ID = 156
RELEASE_BRANCH = "release-ios-vkteams"


class IOS(VKTeamsPlatform):
    def __init__(self, product):
        super().__init__(product)

    def process(self, bot, event, back_markup, version, product_raw):
        if product_raw == 'onpremise':
            product_jira_structure_name = 'VK Teams On-Premise'
        elif product_raw == 'saas':
            product_jira_structure_name = 'VK Teams SaaS'
        else:
            product_jira_structure_name = ""

        if not product_jira_structure_name:
            bot.edit_text(
                chat_id=event.from_chat,
                msg_id=event.data['message'].get('msgId'),
                text="Не удалось получить информацию по платформе iOS "
                     f"для версии {version} продукта {product_jira_structure_name}",
                parse_mode="HTML",
                inline_keyboard_markup=f"{json.dumps(back_markup)}"
            )
            return

        bot.edit_text(
            chat_id=event.from_chat,
            msg_id=event.data['message'].get('msgId'),
            text="Загрузка... Ожидайте ⏳",
            parse_mode="HTML",
            inline_keyboard_markup=f"{json.dumps(back_markup)}"
        )

        latest_rc_name, rc_status, rc_issue_key, rc_version = self.get_latest_release_candidate(
            product=product_jira_structure_name,
            version=version,
            bot=bot,
            event=event,
            back_markup=back_markup
        )

        if not latest_rc_name or not rc_status or not rc_issue_key or not rc_version:

            bot.edit_text(
                chat_id=event.from_chat,
                msg_id=event.data['message'].get('msgId'),
                text="Не удалось получить информацию по платформе iOS "
                     f"для версии {version} продукта {product_jira_structure_name}",
                parse_mode="HTML",
                inline_keyboard_markup=f"{json.dumps(back_markup)}"
            )
            return

        bot.edit_text(
            chat_id=event.from_chat,
            msg_id=event.data['message'].get('msgId'),
            text=self._create_message_status_of_release(
                product_jira_structure_name, version, rc_issue_key, latest_rc_name, rc_status, self._ensure_patch_version(rc_version)
            ),
            parse_mode="HTML",
            inline_keyboard_markup=f"{json.dumps(back_markup)}"
        )

    @retry_in_rc(max_attempts=20, notify_after=7)
    def get_latest_release_candidate(self, product, version, bot, event, back_markup):
        return self.product.jira_client.parse_structure_get_latest_release_candidate(
            structure_id=self.structure_id,
            base_version=version,
            platform="iOS",
            product=product,
        )

    def _create_message_status_of_release(
            self, product_jira_structure_name, version, rc_issue_key, latest_rc_name, rc_status, rc_version
    ):
        return f"""Для платформы iOS продукта {product_jira_structure_name} версии {version}:

актуальный релиз-кандидат:
<a href='https://example.org'>{latest_rc_name}</a>
сейчас в статусе: {rc_status}

Актуальная релиз ветка для этого Релиз Кандидата:
<pre>{RELEASE_BRANCH}-{rc_version}</pre>
<a href='https://example.org'>смотреть в Gitlab</a>"""

    def _ensure_patch_version(self, version):
        parts = version.split('.')
        while len(parts) < 3:
            parts.append('0')
        true_build_version = '.'.join(parts)
        return true_build_version

    async def process_jira_task_to_release(
            self, jira_task_key, release_branch, bot, chat_id_to_reply, gitlab_url, jira_url):
        result = await self.product.gitlab_client.process_merge_requests(
            project_id=VK_TEAMS_IOS_PROJECT_ID,
            search_str=jira_task_key,
            target_branch=release_branch,
            gitlab_url=gitlab_url,
            gitlab_project="проект_в_корпоративном_гитлаб",
            jira_url=jira_url,
        )
        bot.send_text(
            chat_id=chat_id_to_reply,
            text=result,
            parse_mode='HTML'
        )

    async def check_release_branch_contains_task(
            self, jira_task_key, release_branch, bot, chat_id_to_reply):
        result = await self.product.gitlab_client.search_commits_in_branch(
            project_id=VK_TEAMS_IOS_PROJECT_ID,
            search_str=jira_task_key,
            branch_name=release_branch,
        )
        bot.send_text(
            chat_id=chat_id_to_reply,
            text=result,
            parse_mode='HTML'
        )
