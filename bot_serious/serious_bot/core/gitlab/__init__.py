from http import HTTPStatus

from loguru import logger
from pydantic import BaseModel


from prosto_gitlab_client.client import GitlabClient


class CherryPickModel(BaseModel):
    branch: str


class GitlabClientExtended(GitlabClient):

    def _make_headers(self, headers: dict | None = None) -> dict:
        result_headers = headers or {}
        result_headers.update(
            {
                'Content-Type': 'application/json',
                'PRIVATE-TOKEN': self.token,
            },
        )
        if self.global_request_id:
            result_headers['X-MCS-Request-ID'] = self.global_request_id
        return result_headers

    async def search_commits_in_branch(self, project_id: str, branch_name: str, search_str: str) -> str:
        url = f'projects/{project_id}/repository/commits?ref_name={branch_name}'
        response = await self.get(url)
        if response.status != HTTPStatus.OK:
            raise Exception(f"Failed to get commits: {response.status}")
        commits = await response.json()
        result = "Коммиты найдены:\n\n"
        present = False
        for commit in commits:
            if search_str in commit['title']:
                present = True
                result += f"{commit['title']}\n"
        if present:
            return result
        return f"В ветке {branch_name} коммитов из {search_str} не найдено"

    async def find_closed_merge_request(self, project_id: str, search_str: str):
        url = f'projects/{project_id}/merge_requests?state=merged'
        print(f"Requesting URL: {url}")
        response = await self.get(url)
        if response.status != HTTPStatus.OK:
            raise Exception(f"Failed to get merge requests: {response.status}")
        merge_requests = await response.json()
        for mr in merge_requests:
            if search_str in mr['title']:
                return mr
        return None

    async def get_merge_request_commits(self, project_id: str, merge_request_iid: int):
        response = await self.get(f'projects/{project_id}/merge_requests/{merge_request_iid}/commits')
        if response.status != HTTPStatus.OK:
            raise Exception(f"Failed to get commits: {response.status}")
        return await response.json()

    async def cherry_pick_commit(self, project_id: str, commit_sha: str, target_branch: str):
        cherry_pick_data = CherryPickModel(branch=target_branch)
        response = await self.post(
            f'projects/{project_id}/repository/commits/{commit_sha}/cherry_pick',
            model_in=cherry_pick_data
        )
        if response.status != HTTPStatus.CREATED:
            error_msg = await response.json()
            logger.error(f"Failed to cherry-pick commit {commit_sha}: {error_msg}")
            return False, error_msg
        return True, await response.json()

    async def get_user_public_email(self, user_id: int):
        response = await self.get(f'users/{user_id}')
        if response.status != HTTPStatus.OK:
            raise Exception(f"Failed to get user info: {response.status}")
        user_info = await response.json()
        return user_info.get('public_email', 'No public email available')

    async def process_merge_requests(
            self, project_id: str, search_str: str, target_branch: str,
            gitlab_url: str, gitlab_project: str, jira_url: str
    ) -> str:
        mr = await self.find_closed_merge_request(project_id, search_str)
        if not mr:
            return ("Merge Request для данного таска не найден: возможно он ещё открыт или не создан.\n\n"
                    "Свяжитесь с разработчиком по данной задаче: "
                    f"<a href='https://example.org'>{search_str}</a>")
        commits = await self.get_merge_request_commits(project_id, mr['iid'])
        for commit in sorted(commits, key=lambda x: x['created_at']):
            if "Merge" not in commit['title']:
                success, result = await self.cherry_pick_commit(project_id, commit['id'], target_branch)
                if not success:
                    assignee_id = mr.get('assignee', {}).get('id')
                    if assignee_id:
                        public_email = await self.get_user_public_email(assignee_id)
                        return ("Не получилось выполнить cherry-pick таски, обратитесь к разработчику"
                                f"<a>@[{public_email}]</a>")
                    else:
                        return "Не получилось выполнить cherry-pick таски, обратитесь к разработчику"
        return ("✅ Всё получилось!\n\n"
                "Историю ветки можно посмотреть тут:\n"
                f"<a href='https://example.org'>{target_branch}</a>")
