"""
Bitbucket adapter for fetching PR data.
"""
import re
from typing import Dict, Optional
from datetime import datetime
from atlassian import Bitbucket
import logging

from src.data_preparation.base_adapter import BasePlatformAdapter, PullRequest, FileChange
from src.config.settings import settings

logger = logging.getLogger(__name__)


class BitbucketAdapter(BasePlatformAdapter):
    """Adapter for Bitbucket API."""

    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        """Initialize Bitbucket adapter."""
        super().__init__(
            token=None,
            username=username or settings.bitbucket_username,
            password=password or settings.bitbucket_password
        )

        self.username = self.extra_config.get('username')
        self.password = self.extra_config.get('password')

        if not self.username or not self.password:
            logger.warning("No Bitbucket credentials provided.")
            self.client = None
        else:
            self.client = Bitbucket(
                url=settings.bitbucket_url,
                username=self.username,
                password=self.password,
                cloud=True
            )

    def parse_url(self, url: str) -> Dict[str, str]:
        """
        Parse Bitbucket PR URL.

        Example: https://bitbucket.org/owner/repo/pull-requests/123
        """
        pattern = r"bitbucket\.org/([^/]+)/([^/]+)/pull-requests/(\d+)"
        match = re.search(pattern, url)

        if not match:
            raise ValueError(f"Invalid Bitbucket PR URL: {url}")

        return {
            "workspace": match.group(1),
            "repo": match.group(2),
            "pr_number": int(match.group(3))
        }

    def fetch_pull_request(self, url: str) -> PullRequest:
        """Fetch PR details from Bitbucket."""
        if not self.client:
            raise ValueError("Bitbucket client not initialized. Provide credentials.")

        try:
            parsed = self.parse_url(url)
            workspace = parsed['workspace']
            repo = parsed['repo']
            pr_number = parsed['pr_number']

            logger.info(f"Fetching Bitbucket PR: {workspace}/{repo}#{pr_number}")

            # Note: The atlassian-python-api library has limited Bitbucket Cloud support
            # This is a simplified implementation
            pr_data = self.client.get_pullrequest(
                workspace, repo, pr_number
            )

            # Get file changes (simplified - actual implementation would need more API calls)
            files_changed = []

            pull_request = PullRequest(
                platform="bitbucket",
                id=str(pr_data.get('id', pr_number)),
                number=pr_number,
                title=pr_data.get('title', ''),
                description=pr_data.get('description', ''),
                author=pr_data.get('author', {}).get('display_name', 'unknown'),
                created_at=datetime.fromisoformat(
                    pr_data.get('created_on', '').replace('Z', '+00:00')
                ) if pr_data.get('created_on') else datetime.now(),
                updated_at=datetime.fromisoformat(
                    pr_data.get('updated_on', '').replace('Z', '+00:00')
                ) if pr_data.get('updated_on') else datetime.now(),
                state=pr_data.get('state', 'unknown'),
                source_branch=pr_data.get('source', {}).get('branch', {}).get('name', ''),
                target_branch=pr_data.get('destination', {}).get('branch', {}).get('name', ''),
                repository=f"{workspace}/{repo}",
                url=url,
                files_changed=files_changed,
                commits_count=0,  # Would need additional API call
                additions=0,
                deletions=0,
                changed_files=len(files_changed),
                labels=[],
                language=None
            )

            logger.info(f"Successfully fetched Bitbucket PR")
            return pull_request

        except Exception as e:
            logger.error(f"Error fetching Bitbucket PR: {e}")
            raise

    def get_file_content(self, repo: str, filepath: str, ref: str) -> str:
        """Get file content from Bitbucket."""
        if not self.client:
            raise ValueError("Bitbucket client not initialized.")

        try:
            # Implementation would depend on workspace/repo parsing
            raise NotImplementedError("Bitbucket file content retrieval not fully implemented")

        except Exception as e:
            logger.error(f"Error fetching file content: {e}")
            raise

    def post_review_comment(self, pr_url: str, comment: str) -> bool:
        """Post a review comment on Bitbucket PR."""
        if not self.client:
            logger.error("Bitbucket client not initialized.")
            return False

        try:
            # Implementation would require proper API endpoint
            logger.warning("Bitbucket comment posting not fully implemented")
            return False

        except Exception as e:
            logger.error(f"Error posting review comment: {e}")
            return False

