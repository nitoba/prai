from base64 import b64encode
from typing import List

from requests import get, post

from env import env


class AzureDevopsService:
    def __init__(self):
        self.organization = env.AZURE_DEVOPS_ORGANIZATION
        self.project = env.AZURE_DEVOPS_PROJECT
        self.repository_id = env.AZURE_DEVOPS_REPOSITORY_ID
        self.auth_token = b64encode(
            f':{env.AZURE_DEVOPS_PAT}'.encode()
        ).decode()

    def get_diff(
        self, source_branch: str, target_branch: str, repository_id: str
    ) -> str:
        url = f'https://dev.azure.com/{self.organization}/{self.project}/_apis/git/repositories/{repository_id}/diffs/commits?baseVersion={target_branch}&targetVersion={source_branch}&api-version=6.0'

        data = get(url, headers={'Authorization': f'Basic {self.auth_token}'})

        if data.status_code != 200:
            raise Exception(f'Error to get diff: {data.status_code}')

        data = data.json()

        changes = '\n\n'.join([
            f"File: {change['item']['path']}\nChangeType: {change['changeType']}"
            for change in data['changes']
        ])

        return changes

    def get_commit_messages(
        self, source_branch: str, target_branch: str, repository_id: str
    ) -> List[str]:
        url = f'https://dev.azure.com/{self.organization}/{self.project}/_apis/git/repositories/{repository_id}/commitsBatch?api-version=6.0'

        payload = {
            'itemVersion': {'versionType': 'branch', 'version': target_branch},
            'compareVersion': {
                'versionType': 'branch',
                'version': source_branch,
            },
            'top': 1000,
        }

        data = post(
            url,
            json=payload,
            headers={
                'Authorization': f'Basic {self.auth_token}',
                'Content-Type': 'application/json',
            },
        )

        if data.status_code != 200:
            raise Exception(
                f'Error fetching commits: {data.status_code} - {data.text}'
            )

        data = data.json()

        # print('Azure DevOps commitsBatch response:', data)

        commit_messages = [commit['comment'] for commit in data['value']]
        return commit_messages

    def create_pull_request(
        self,
        source_branch: str,
        target_branch: str,
        pr_title: str,
        pr_body: str,
    ):
        url = f'https://dev.azure.com/{self.organization}/{self.project}/_apis/git/repositories/{self.repository_id}/pullrequests?api-version=6.0'

        payload = {
            'sourceRefName': f'refs/heads/{source_branch}',
            'targetRefName': f'refs/heads/{target_branch}',
            'title': pr_title,
            'description': pr_body,
        }

        data = post(
            url,
            json=payload,
            headers={
                'Authorization': f'Basic {self.auth_token}',
                'Content-Type': 'application/json',
            },
        )

        return data
