"""
GitHub adapter for fetching PR data.
"""
import re
from typing import Dict, Optional
from datetime import datetime
from github import Github, GithubException
import logging

from src.data_preparation.base_adapter import BasePlatformAdapter, PullRequest, FileChange
from src.config.settings import settings

logger = logging.getLogger(__name__)


class GitHubAdapter(BasePlatformAdapter):
    """Adapter for GitHub API."""

    def __init__(self, token: Optional[str] = None):
        """Initialize GitHub adapter."""
        super().__init__(token or settings.github_token)
        if not self.token:
            logger.warning("No GitHub token provided. API rate limits will be restricted.")
        self.client = Github(self.token) if self.token else Github()

    def parse_url(self, url: str) -> Dict[str, str]:
        """
        Parse GitHub PR URL.

        Example: https://github.com/owner/repo/pull/123
        """
        pattern = r"github\.com/([^/]+)/([^/]+)/pull/(\d+)"
        match = re.search(pattern, url)

        if not match:
            raise ValueError(f"Invalid GitHub PR URL: {url}")

        return {
            "owner": match.group(1),
            "repo": match.group(2),
            "pr_number": int(match.group(3))
        }

    def fetch_pull_request(self, url: str) -> PullRequest:
        """Fetch PR details from GitHub."""
        try:
            parsed = self.parse_url(url)
            repo_name = f"{parsed['owner']}/{parsed['repo']}"
            pr_number = parsed['pr_number']

            logger.info(f"Fetching GitHub PR: {repo_name}#{pr_number}")

            # Get repository and PR
            repo = self.client.get_repo(repo_name)
            pr = repo.get_pull(pr_number)

            # Get file changes
            files_changed = []
            for file in pr.get_files():
                files_changed.append(FileChange(
                    filename=file.filename,
                    status=file.status,
                    additions=file.additions,
                    deletions=file.deletions,
                    changes=file.changes,
                    patch=file.patch,
                    previous_filename=file.previous_filename
                ))

            # Determine primary language
            language = repo.language

            # Get labels
            labels = [label.name for label in pr.labels]

            pull_request = PullRequest(
                platform="github",
                id=str(pr.id),
                number=pr.number,
                title=pr.title,
                description=pr.body or "",
                author=pr.user.login,
                created_at=pr.created_at,
                updated_at=pr.updated_at,
                state=pr.state,
                source_branch=pr.head.ref,
                target_branch=pr.base.ref,
                repository=repo_name,
                url=url,
                files_changed=files_changed,
                commits_count=pr.commits,
                additions=pr.additions,
                deletions=pr.deletions,
                changed_files=pr.changed_files,
                labels=labels,
                language=language
            )

            logger.info(f"Successfully fetched PR with {len(files_changed)} files changed")
            return pull_request

        except GithubException as e:
            logger.error(f"GitHub API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error fetching GitHub PR: {e}")
            raise

    def get_file_content(self, repo: str, filepath: str, ref: str) -> str:
        """Get file content from GitHub."""
        try:
            repository = self.client.get_repo(repo)
            content = repository.get_contents(filepath, ref=ref)

            if isinstance(content, list):
                raise ValueError(f"{filepath} is a directory, not a file")

            return content.decoded_content.decode('utf-8')

        except Exception as e:
            logger.error(f"Error fetching file content: {e}")
            raise

    def post_review_comment(self, pr_url: str, comment: str) -> bool:
        """Post a review comment on GitHub PR."""
        try:
            parsed = self.parse_url(pr_url)
            repo_name = f"{parsed['owner']}/{parsed['repo']}"
            pr_number = parsed['pr_number']

            repo = self.client.get_repo(repo_name)
            pr = repo.get_pull(pr_number)

            # Post as a regular comment
            pr.create_issue_comment(comment)

            logger.info(f"Posted review comment to PR #{pr_number}")
            return True

        except Exception as e:
            logger.error(f"Error posting review comment: {e}")
            return False

    def get_rate_limit(self) -> Dict[str, int]:
        """Get current rate limit status."""
        rate_limit = self.client.get_rate_limit()
        return {
            "remaining": rate_limit.core.remaining,
            "limit": rate_limit.core.limit,
            "reset": rate_limit.core.reset
        }

