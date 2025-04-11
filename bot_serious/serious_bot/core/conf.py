from serious_bot.core.config import Conf as TemplateConf


class Conf(TemplateConf):

    @property
    def bot_token(self) -> str:
        return self.get('VKT_BOT_TOKEN')

    @property
    def bot_id(self) -> str:
        return self.get('VKT_BOT_ID')

    @property
    def bot_api_url(self) -> str:
        return self.get("VKT_BASE_URL")

    @property
    def jira_base_url(self) -> str:
        return self.get('JIRA_BASE_URL')

    @property
    def jira_token(self) -> str:
        return self.get('JIRA_TOKEN')

    @property
    def gitlab_base_url(self) -> str:
        return self.get('GITLAB_BASE_URL')

    @property
    def gitlab_token(self) -> str:
        return self.get('GITLAB_TOKEN')

    @property
    def admins(self) -> []:
        return self.get("ADMINS").split(',')

    @property
    def vk_tech_products_filter_id(self) -> []:
        return self.get("VK_TECH_PRODUCTS_FILTER_ID")

    @property
    def vk_teams_product_card_issue_key(self) -> []:
        return self.get("VK_TEAMS")

    @property
    def vk_workspace_product_card_issue_key(self) -> []:
        return self.get("VK_WORKSPACE")
