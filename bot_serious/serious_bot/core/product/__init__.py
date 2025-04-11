import uuid

from loguru import logger

from serious_bot.core.jira import JiraClient
from serious_bot.core.gitlab import GitlabClientExtended


def _get_processed_releases(issue) -> []:
    releases_in_process_now = []
    for processed_release in [
        subtask.fields.summary for subtask in issue.fields.subtasks if subtask.fields.status.name.lower() in [
            'planning', 'active'
        ]
    ]:
        releases_in_process_now.append(processed_release)
    return releases_in_process_now


class Product:
    def __init__(
        self,
        ticket_key: str,
        jira_url: str,
        jira_token: str,
        gitlab_url: str,
        gitlab_token: str,
    ) -> None:
        self.ticket_key = ticket_key

        self.jira_url = jira_url
        self.jira_client = JiraClient(
            base_url=jira_url,
            token=jira_token,
            logger=logger,
        )

        self.gitlab_url = gitlab_url
        self.gitlab_client = GitlabClientExtended(
            api_url=f"{gitlab_url}/api/v4/",
            token=gitlab_token,
            global_request_id=str(uuid.uuid4()),
        )

        self.releases_in_process_now = []
        self.allowed_platforms = []

        self.logger = logger

    def prepare(self) -> None:
        self.logger.warning("prepare method is not implemented")

    def parse_jira_product_card(self):
        issue = self.jira_client.jira.issue(id=self.ticket_key, fields=['subtasks'])
        self.releases_in_process_now = _get_processed_releases(issue)

    def process_product(self, bot, bot_id, event, back_markup):
        self.logger.warning("process_product method is not implemented")

    def select_platform(self, bot, event, version, name):
        self.logger.warning("select_platform method is not implemented")

    def process_platform(self, bot, event, platform, version, name):
        self.logger.warning("process_platform method is not implemented")

    def cleanup(self) -> None:
        self.logger.warning("Cleanup method is not implemented")
