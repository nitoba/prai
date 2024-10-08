from langchain_core.tools import tool

from azure_devops_service import AzureDevopsService


@tool
def fetch_diff_in_code(
    source_branch: str, target_branch: str, repository_name: str
) -> str:
    """
    Search for diff in code based on source_branch, target_branch, and repository_name.

    Args:
        source_branch str: The source branch to compare.
        target_branch str: The target branch to compare.
        repository_name str: The name of the repository to search.
    Returns:
        str: The diff of the code between the source and target branches.
    """
    azure_devops_service = AzureDevopsService()
    diff = azure_devops_service.get_diff(
        source_branch, target_branch, repository_name
    )
    return diff


@tool
def fetch_for_commit_messages(
    source_branch: str, target_branch: str, repository_name: str
) -> list[str]:
    """
    Search for commit messages in the repository based on source_branch, target_branch, and repository_name.

    Args:
        source_branch str: The source branch to compare.
        target_branch str: The target branch to compare.
        repository_name str: The name of the repository to search.
    Returns:
        list[str]: The list of commit messages in the repository between the source and target branches.
    """
    azure_devops_service = AzureDevopsService()
    commit_messages = azure_devops_service.get_commit_messages(
        source_branch, target_branch, repository_name
    )

    return commit_messages


pr_tools = [fetch_diff_in_code, fetch_for_commit_messages]
