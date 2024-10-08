from llm import llm


class PullRequestService:
    def __init__(self, azure_devops_service):
        self.azure_devops_service = azure_devops_service
        self.model = llm

    def handle_pull_request(self, dto):
        source_branch = dto.source_branch
        target_branch = dto.target_branch

        # Get changes between branches
        changes = self.azure_devops_service.get_diff(
            source_branch, target_branch, dto.repository_name
        )

        commit_messages = self.azure_devops_service.get_commit_messages(
            source_branch, target_branch, dto.repository_name
        )

        # Generate PR description using AI
        pr_body = self.generate_pull_request_description(
            changes, commit_messages
        )

        return pr_body
